include("./MatchingFunctions.jl")
using ArgParse
using CSV
using DataFrames
using DataFramesMeta
using Dates
using Logging
using Random
using Statistics
using .MatchingFunctions

function main()
    # get time to synchronize solutions
    now_time = string(Dates.format(now(), "yyyymmdd_HHMMSS"))
    parser = ArgParseSettings(description="The settings of Greedy Search for refinement")
    @add_arg_table! parser begin
        "--init_sol"
        help = "name of the initial solution file (without extension)"
        arg_type = String
        default = "5765447_20250107_101550.csv"

        "--seed"
        help = "random seed"
        arg_type = Int
        default = 392

        "--max_iter"
        help = "maximum number of iterations"
        arg_type = Int
        default = 1000
    end
    # init the random seed and file path
    args = parse_args(parser)
    Random.seed!(args["seed"])
    path_male = joinpath("..", "data", "male_connectome_graph.csv")
    path_female = joinpath("..", "data", "female_connectome_graph.csv")
    path_sol = joinpath("..", "sol", args["init_sol"])
    # read the male, female connection data and initial solution file
    df_male, df_female, df_sol = read_data(path_male, path_female, path_sol)
    """get the dictionary of male, female edges and male and female matching
       male_edges (Dict): ("From Node ID", "To Node ") -> Weight
       female_edges (Dict): ("From Node ID", "To Node ") -> Weight
       matching (Dict): "Male Node ID" -> "Female Node ID"
       matching_female (Dict): "Female Node ID" -> "Male Node ID"
    """
    male_edges = Dict(zip(zip(df_male."From Node ID", df_male."To Node ID"), df_male.Weight))
    female_edges = Dict(zip(zip(df_female."From Node ID", df_female."To Node ID"), df_female.Weight))
    matching = Dict(zip(df_sol."Male Node ID", df_sol."Female Node ID"))
    matching_female = Dict(zip(df_sol."Female Node ID", df_sol."Male Node ID"))

    # get the list of unique male and female edges
    unique_edges_female = collect(keys(female_edges))
    unique_edges_male = collect(keys(male_edges))
    # initialize the current score
    cur_score = calculate_final_score(male_edges, female_edges, matching)
    new_matching = copy(matching)
    new_matching_female = copy(matching_female)

    # main greedy search loop
    steps = 0
    max_iter = args["max_iter"]
    println("Initial score: ", cur_score)

    for iter in 1:max_iter
        steps += 1
        improved = false

        # try all possible swaps (male side) – greedy
        for edge in unique_edges_male
            male_edge = edge
            delta, new_matching_temp = cal_delta_random_swap(male_edge, df_male, female_edges, new_matching)
            if delta > 0
                cur_score = cur_score + delta
                new_matching = new_matching_temp
                new_matching_female = Dict(zip(values(new_matching), keys(new_matching)))
                df_matching = transfer_df_matching(new_matching)
                save_sol(df_matching, cur_score, now_time)
                improved = true
                println("Improved to ", cur_score, " at step ", steps)
                break  # restart from beginning after improvement
            end
        end

        # if no improvement on male side, try female side
        if !improved
            for edge in unique_edges_female
                random_female_edge = edge
                # get corresponding male edge
                male_edge = (new_matching_female[random_female_edge[1]], new_matching_female[random_female_edge[2]])
                delta, new_matching_temp = cal_delta_random_swap(male_edge, df_male, female_edges, new_matching)
                if delta > 0
                    cur_score = cur_score + delta
                    new_matching = new_matching_temp
                    new_matching_female = Dict(zip(values(new_matching), keys(new_matching)))
                    df_matching = transfer_df_matching(new_matching)
                    save_sol(df_matching, cur_score, now_time)
                    improved = true
                    println("Improved to ", cur_score, " at step ", steps)
                    break  # restart after improvement
                end
            end
        end

        # if no improvement in either side, break (local optimum reached)
        if !improved
            println("No further improvement found. Stopping at score ", cur_score)
            break
        end
    end

    println("Final score: ", cur_score)
end

main()