using CSV, DataFrames, LinearAlgebra, Statistics

# 1. Завантажуємо benchmark як основу
benchmark_path = normpath(joinpath(@__DIR__, "..", "..", "data", "benchmarks", "benchmark_matching.csv"))
df_bench = CSV.read(benchmark_path, DataFrame)
matching = Dict(df_bench."Male Node ID" .=> df_bench."Female Node ID")

# 2. Завантажуємо графи
male_path = normpath(joinpath(@__DIR__, "..", "..", "data", "raw", "male_connectome_graph.csv"))
female_path = normpath(joinpath(@__DIR__, "..", "..", "data", "raw", "female_connectome_graph.csv"))
df_male = CSV.read(male_path, DataFrame)
df_female = CSV.read(female_path, DataFrame)

# 3. Обчислюємо ознаки (наприклад, degree centrality) для кожного нейрона
function compute_node_features(df)
    nodes = unique(vcat(df."From Node ID", df."To Node ID"))
    features = Dict{String, Vector{Float64}}()
    for node in nodes
        # Прості ознаки: in-degree, out-degree, weighted in/out
        in_deg = count(row -> row."To Node ID" == node, eachrow(df))
        out_deg = count(row -> row."From Node ID" == node, eachrow(df))
        in_w = sum(row -> row."To Node ID" == node ? row.Weight : 0, eachrow(df))
        out_w = sum(row -> row."From Node ID" == node ? row.Weight : 0, eachrow(df))
        features[node] = [Float64(in_deg), Float64(out_deg), Float64(in_w), Float64(out_w)]
    end
    return features
end

male_features = compute_node_features(df_male)
female_features = compute_node_features(df_female)

# 4. Робимо "розумні" обміни
# Для кожної пари (m, f) пробуємо знайти іншу пару (m', f'), 
# щоб обмін покращив сумарну схожість ознак.

male_nodes = collect(keys(matching))
female_nodes = values(matching)

# Список усіх жіночих вершин (для перевірки унікальності)
all_female = collect(keys(female_features))

for i in 1:length(male_nodes)
    m = male_nodes[i]
    f = matching[m]
    
    # Для цього m знаходимо найбільш схожу жіночу вершину (за ознаками)
    best_f = f
    best_score = -Inf
    for f_candidate in all_female
        # Пропускаємо, якщо f_candidate вже зайнята
        if f_candidate in values(matching) && f_candidate != f
            continue
        end
        score = -norm(male_features[m] .- female_features[f_candidate])
        if score > best_score
            best_score = score
            best_f = f_candidate
        end
    end
    
    # Якщо знайшли кращу пару, то робимо обмін
    if best_f != f
        # Знаходимо m', який зараз відповідає best_f
        m_prime = nothing
        for (mm, ff) in matching
            if ff == best_f
                m_prime = mm
                break
            end
        end
        # Обмін: m -> best_f, m_prime -> f
        if m_prime != nothing
            matching[m] = best_f
            matching[m_prime] = f
        end
    end
end

# 5. Зберігаємо результат
out_path = normpath(joinpath(@__DIR__, "..", "..", "output", "solutions", "subit_initial_fixed.csv"))
df_out = DataFrame("Male Node ID" => collect(keys(matching)), "Female Node ID" => collect(values(matching)))
CSV.write(out_path, df_out)
println("Створено $out_path")