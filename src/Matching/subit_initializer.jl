using CSV
using DataFrames
using LinearAlgebra
using Statistics

# ============ 1. Завантаження даних ============
function load_graph(path::String)
    df = CSV.File(path) |> DataFrame
    if "To Node Id" in names(df)
        rename!(df, "To Node Id" => "To Node ID")
    end
    return df
end

male_path = normpath(joinpath(@__DIR__, "..", "..", "data", "raw", "male_connectome_graph.csv"))
female_path = normpath(joinpath(@__DIR__, "..", "..", "data", "raw", "female_connectome_graph.csv"))
benchmark_path = normpath(joinpath(@__DIR__, "..", "..", "data", "benchmarks", "benchmark_matching.csv"))

df_male = load_graph(male_path)
df_female = load_graph(female_path)
df_benchmark = load_graph(benchmark_path)

println("Male edges: ", size(df_male, 1))
println("Female edges: ", size(df_female, 1))
println("Benchmark matches: ", size(df_benchmark, 1))

# ============ 2. Повні списки нейронів (конвертуємо у Vector{String}) ============
male_nodes_all = String.(unique(vcat(df_male."From Node ID", df_male."To Node ID")))
female_nodes_all = String.(unique(vcat(df_female."From Node ID", df_female."To Node ID")))
# Додаємо з benchmark, якщо якісь відсутні
male_nodes_all = String.(unique(vcat(male_nodes_all, df_benchmark."Male Node ID")))
female_nodes_all = String.(unique(vcat(female_nodes_all, df_benchmark."Female Node ID")))

println("Total male nodes: ", length(male_nodes_all))
println("Total female nodes: ", length(female_nodes_all))

# ============ 3. Обчислення ознак ============
function compute_features(df::DataFrame, nodes_all::Vector{String})
    n = length(nodes_all)
    idx = Dict(node => i for (i, node) in enumerate(nodes_all))
    in_deg = zeros(Int, n)
    out_deg = zeros(Int, n)
    in_w = zeros(Float64, n)
    out_w = zeros(Float64, n)

    for row in eachrow(df)
        src = String(row."From Node ID")
        dst = String(row."To Node ID")
        w = row.Weight
        if haskey(idx, src) && haskey(idx, dst)
            i = idx[src]
            j = idx[dst]
            out_deg[i] += 1
            in_deg[j] += 1
            out_w[i] += w
            in_w[j] += w
        end
    end

    features = Dict{String, Vector{Float64}}()
    for node in nodes_all
        i = idx[node]
        features[node] = [
            Float64(in_deg[i]),
            Float64(out_deg[i]),
            Float64(in_w[i]),
            Float64(out_w[i]),
            Float64(in_deg[i] + out_deg[i]),
            Float64(in_w[i] + out_w[i])
        ]
    end
    return features
end

male_features = compute_features(df_male, male_nodes_all)
female_features = compute_features(df_female, female_nodes_all)

# ============ 4. Нормалізація ============
function normalize_features(features::Dict{String, Vector{Float64}})
    node_list = collect(keys(features))
    all_vectors = reduce(vcat, [reshape(features[node], 1, :) for node in node_list])
    means = vec(mean(all_vectors, dims=1))
    stds = vec(std(all_vectors, dims=1))
    stds[stds .== 0] .= 1
    normalized = Dict{String, Vector{Float64}}()
    for (i, node) in enumerate(node_list)
        vec = (all_vectors[i, :] .- means) ./ stds
        normalized[node] = vec
    end
    return normalized
end

male_norm = normalize_features(male_features)
female_norm = normalize_features(female_features)

# ============ 5. Жадібне призначення ============
all_male = sort(male_nodes_all)
all_female = sort(female_nodes_all)

used_female = falses(length(all_female))
female_idx = Dict(node => i for (i, node) in enumerate(all_female))
male_vectors = [male_norm[node] for node in all_male]
female_vectors = [female_norm[node] for node in all_female]

matching = Dict{String, String}()

for i in 1:length(all_male)
    male_node = all_male[i]
    mv = male_vectors[i]
    best_dist = Inf
    best_j = -1

    for j in 1:length(all_female)
        if !used_female[j]
            dist = norm(mv - female_vectors[j])
            if dist < best_dist
                best_dist = dist
                best_j = j
            end
        end
    end

    if best_j == -1
        # Якщо всі використані (не повинно статися), беремо першу невикористану
        for j in 1:length(all_female)
            if !used_female[j]
                best_j = j
                break
            end
        end
    end

    if best_j != -1
        matching[male_node] = all_female[best_j]
        used_female[best_j] = true
    else
        # Крайній випадок: беремо першу жіночу (нехай навіть уже використану)
        matching[male_node] = all_female[1]
    end
end

println("Matching size: ", length(matching))

# ============ 6. Збереження ============
out_path = normpath(joinpath(@__DIR__, "..", "..", "output", "solutions", "subit_initial.csv"))
df_out = DataFrame("Male Node ID" => collect(keys(matching)), "Female Node ID" => collect(values(matching)))
CSV.write(out_path, df_out, header=true)

println("Initial solution saved to ", out_path)