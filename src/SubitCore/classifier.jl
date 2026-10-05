using CSV
using DataFrames
using SparseArrays
using LinearAlgebra
using Statistics

println("=== SUBIT-64 Connectome Classification Pipeline ===")
println("Loading male connectome data...")

male_path = normpath(joinpath(@__DIR__, "..", "..", "data", "raw", "male_connectome_graph.csv"))
if !isfile(male_path)
    error("File not found: $male_path")
end

# 1. Читання графа
df_male = CSV.File(male_path) |> DataFrame
if "To Node Id" in names(df_male)
    rename!(df_male, "To Node Id" => "To Node ID")
end

println("Loaded $(nrow(df_male)) edges.")

# 2. Унікальні вершини та індексація
from_nodes = String.(df_male."From Node ID")
to_nodes = String.(df_male."To Node ID")
weights = Float64.(df_male.Weight)

unique_nodes = sort(unique(vcat(from_nodes, to_nodes)))
N = length(unique_nodes)
println("Total unique neurons N = $N")

node_to_idx = Dict{String, Int}(node => i for (i, node) in enumerate(unique_nodes))
from_idx = [node_to_idx[s] for s in from_nodes]
to_idx = [node_to_idx[d] for d in to_nodes]

# Побудова розрідженої матриці суміжності A[i, j] = вага зв'язку i -> j
A = sparse(from_idx, to_idx, weights, N, N)

# 3. Обчислення метрик вузлів
println("Computing network topological features...")

# Базові ступені та сумарні ваги
out_deg = vec(sum(A .> 0, dims=2))
in_deg = vec(sum(A .> 0, dims=1))
out_weight = vec(sum(A, dims=2))
in_weight = vec(sum(A, dims=1))

# Взаємні (reciprocal) ваги для оцінки локального зворотного зв'язку
# A_recip[i, j] = min(A[i,j], A[j,i])
A_t = sparse(to_idx, from_idx, weights, N, N)
A_min = min.(A, A_t)
recip_weight = vec(sum(A_min, dims=2))
reciprocity_ratio = [s > 0 ? recip_weight[i] / s : 0.0 for (i, s) in enumerate(out_weight .+ in_weight)]

# 4. Обчислення потокового/трофічного рангу (WHEN) через ітераційний PageRank / Flow Rank
# Сенсорні джерела (високий out/in) отримують низький ранг (ранні), моторні стоки - високий (пізні)
println("Computing dynamic flow / trophic ranks...")
flow_bias = [(out_deg[i] - in_deg[i]) / (out_deg[i] + in_deg[i] + 1.0) for i in 1:N]
# Нормалізований PageRank з телепортацією, що враховує сенсорне зміщення
dangling = out_deg .== 0
inv_out = [out_weight[i] > 0 ? 1.0 / out_weight[i] : 0.0 for i in 1:N]

# Простий алгоритм дифузії рангу (50 ітерацій)
rank = copy(flow_bias)
for iter in 1:40
    global rank = 0.85 .* (A' * (rank .* inv_out)) .+ 0.15 .* flow_bias
end
# Масштабуємо ранг до [0, 1]
min_r, max_r = extrema(rank)
norm_rank = (rank .- min_r) ./ (max_r - min_r + 1e-9)

# 5. Квантування за 3 осями SUBIT: WHO, WHERE, WHEN (по 2 біти кожна = 4 класи)
println("Quantizing into SUBIT-64 coordinates...")

function quantize_4(values::Vector{Float64})
    # Квантування за квантилями (0, 1, 2, 3)
    p25 = quantile(values, 0.25)
    p50 = quantile(values, 0.50)
    p75 = quantile(values, 0.75)
    
    classes = zeros(Int, length(values))
    for i in 1:length(values)
        v = values[i]
        if v <= p25
            classes[i] = 0
        elseif v <= p50
            classes[i] = 1
        elseif v <= p75
            classes[i] = 2
        else
            classes[i] = 3
        end
    end
    return classes
end

# Axis 1: WHO (Функціональна спеціалізація: джерело -> інтернейрон -> хаб -> стік)
# Використовуємо сенсорно-моторний баланс та силу зв'язків
who_metric = flow_bias .+ 0.5 .* log10.(out_weight .+ in_weight .+ 1.0)
who_class = quantize_4(who_metric)

# Axis 2: WHERE (Топологічна локалізація: периферія -> локальний кластер -> мостовий -> глобальне ядро)
# Використовуємо комбінацію коефіцієнта реципрокності та повної ваги
where_metric = reciprocity_ratio .+ 0.3 .* log10.(in_deg .* out_deg .+ 1.0)
where_class = quantize_4(where_metric)

# Axis 3: WHEN (Часовий каскад / затримка: ранній вхід -> проміжний -> резонансний -> кінцевий вихід)
when_class = quantize_4(norm_rank)

# Обчислення 6-бітного SUBIT_ID = WHO * 16 + WHERE * 4 + WHEN
subit_id = [who_class[i] * 16 + where_class[i] * 4 + when_class[i] for i in 1:N]
subit_code = [string(string(who_class[i], base=2, pad=2),
                     string(where_class[i], base=2, pad=2),
                     string(when_class[i], base=2, pad=2)) for i in 1:N]

# 6. Збереження результатів класифікації нейронів
out_nodes_path = normpath(joinpath(@__DIR__, "..", "..", "output", "classifications", "male_subit64_nodes.csv"))
df_nodes = DataFrame(
    Node_ID = unique_nodes,
    In_Degree = in_deg,
    Out_Degree = out_deg,
    In_Weight = in_weight,
    Out_Weight = out_weight,
    Flow_Bias = round.(flow_bias, digits=4),
    Reciprocity = round.(reciprocity_ratio, digits=4),
    Trophic_Rank = round.(norm_rank, digits=4),
    WHO = who_class,
    WHERE = where_class,
    WHEN = when_class,
    SUBIT_ID = subit_id,
    SUBIT_Code = subit_code
)
CSV.write(out_nodes_path, df_nodes)
println("Neuron SUBIT-64 classifications saved to: $out_nodes_path")

# 7. Побудова мета-графа перетоку між 64 класами
println("Building 64x64 functional meta-graph...")
meta_matrix = zeros(Float64, 64, 64)
subit_counts = zeros(Int, 64)

for i in 1:N
    s_i = subit_id[i] + 1 # 1-based index in Julia
    subit_counts[s_i] += 1
end

for k in 1:length(from_idx)
    src_subit = subit_id[from_idx[k]] + 1
    dst_subit = subit_id[to_idx[k]] + 1
    meta_matrix[src_subit, dst_subit] += weights[k]
end

# Зберігаємо опис мета-графа у форматі JSON для інтерактивної візуалізації
# Підготуємо списки nodes та links
nodes_json_parts = String[]
who_labels = ["Sensory/Input", "Feedforward Relay", "Integrator/Hub", "Motor/Effector"]
where_labels = ["Peripheral Leaf", "Local Cluster", "Modular Bridge", "Central Core"]
when_labels = ["Early Cascade", "Middle Transit", "Recurrent Attractor", "Terminal Readout"]

for s in 0:63
    w = div(s, 16)
    p = div(s % 16, 4)
    t = s % 4
    code_str = string(string(w, base=2, pad=2), string(p, base=2, pad=2), string(t, base=2, pad=2))
    name = "S$(s) [$code_str]"
    desc = "$(who_labels[w+1]) | $(where_labels[p+1]) | $(when_labels[t+1])"
    cnt = subit_counts[s+1]
    
    push!(nodes_json_parts, """{"id": $s, "code": "$code_str", "name": "$name", "desc": "$desc", "who": $w, "where": $p, "when": $t, "count": $cnt}""")
end

links_json_parts = String[]
# Відбираємо зв'язки з вагою вище порогу або топові
all_links = Tuple{Int, Int, Float64}[]
for src in 0:63
    for dst in 0:63
        w = meta_matrix[src+1, dst+1]
        if w > 0
            push!(all_links, (src, dst, w))
        end
    end
end
sort!(all_links, by=x -> x[3], rev=true)

# Візьмемо топ 250 зв'язків для чіткості візуалізації графа
top_links = all_links[1:min(250, length(all_links))]
for (src, dst, w) in top_links
    push!(links_json_parts, """{"source": $src, "target": $dst, "weight": $(round(w, digits=1))}""")
end

json_content = """{
  "total_neurons": $N,
  "total_edges": $(nrow(df_male)),
  "nodes": [$(join(nodes_json_parts, ",\n    "))],
  "links": [$(join(links_json_parts, ",\n    "))]
}"""

out_json_path = normpath(joinpath(@__DIR__, "..", "..", "output", "metagraphs", "subit64_metagraph.json"))
open(out_json_path, "w") do f
    write(f, json_content)
end
println("SUBIT-64 meta-graph JSON saved to: $out_json_path")

println("\n=== SUMMARY OF SUBIT-64 DISTRIBUTION ===")
println("Top 5 most populated SUBIT states:")
order = sortperm(subit_counts, rev=true)
for idx in 1:min(5, 64)
    s = order[idx] - 1
    w = div(s, 16)
    p = div(s % 16, 4)
    t = s % 4
    code_str = string(string(w, base=2, pad=2), string(p, base=2, pad=2), string(t, base=2, pad=2))
    println("  State #$s ($code_str) - $(subit_counts[s+1]) neurons: $(who_labels[w+1]) / $(where_labels[p+1]) / $(when_labels[t+1])")
end

println("\nDone successfully!")
