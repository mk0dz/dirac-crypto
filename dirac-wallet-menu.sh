run_wallet_command() {
    local cmd="$1"
    local description="$2"
    
    echo "${MAGENTA}$description${RESET}"
    echo "${YELLOW}Command: ${RESET}./dirac-wallet.sh $cmd"
    echo "${GREEN}Output:${RESET}"
    echo "${CYAN}--------------------------------------------------${RESET}"
    
    # Special handling for benchmark command
    if [[ "$cmd" == "benchmark"* ]]; then
        cd dirac-wallet && python -m src.cli $cmd
    else
        cd dirac-wallet && ./dirac-wallet.sh $cmd
    fi
    
    local result=$?
    echo "${CYAN}--------------------------------------------------${RESET}"
    cd ..
    
    if [ $result -eq 0 ]; then
        print_success "Command executed successfully"
    else
        print_error "Command failed with exit code $result"
    fi
    
    wait_for_key
    return $result
}

run_benchmarks_menu() {
    clear_screen
    echo "${BOLD}Run Performance Benchmarks${RESET}"
    echo ""
    
    echo "Select benchmark option:"
    echo "1) Run full benchmark suite"
    echo "2) Run with custom iterations"
    echo "3) View previous benchmark summary"
    echo ""
    read -p "Select option [1-3] (default: 1): " bench_option
    
    case "$bench_option" in
        2)
            read -p "Enter number of iterations: " iterations
            if [[ ! "$iterations" =~ ^[0-9]+$ ]]; then
                print_error "Invalid number of iterations"
                wait_for_key
                return 1
            fi
            echo "${YELLOW}Warning: Benchmarks may take several minutes to complete.${RESET}"
            read -p "Do you want to continue? [y/N]: " CONFIRM
            if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
                run_wallet_command "benchmark run --iterations $iterations" "Running benchmarks with $iterations iterations..."
            else
                print_info "Benchmarks cancelled"
                wait_for_key
            fi
            ;;
        3)
            echo "Looking for benchmark results..."
            if [ -f "dirac-wallet/benchmark_results/benchmark_results.json" ]; then
                run_wallet_command "benchmark summary dirac-wallet/benchmark_results/benchmark_results.json" "Viewing benchmark summary..."
            else
                print_error "No benchmark results found"
                wait_for_key
            fi
            ;;
        *)
            echo "${YELLOW}Warning: Benchmarks may take several minutes to complete.${RESET}"
            read -p "Do you want to continue? [y/N]: " CONFIRM
            if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
                run_wallet_command "benchmark run" "Running benchmarks..."
            else
                print_info "Benchmarks cancelled"
                wait_for_key
            fi
            ;;
    esac
} 