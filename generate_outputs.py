import os
from student_utils import input_file_to_instance, analyze_solution, write_ptp_solution_to_out
from ptp_solver import ptp_solver

def main():
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)

    # Get all input files
    input_dir = "inputs"
    input_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.in')])

    print("Generating outputs for all input files...\n")

    for input_file in input_files:
        input_path = os.path.join(input_dir, input_file)
        print(f"Processing {input_file}...")

        try:
            # Load the instance
            G, H, alpha = input_file_to_instance(input_path)

            # Solve the problem
            tour, pickups = ptp_solver(G, H, alpha)

            # Validate the solution
            is_valid, drive_cost, walk_cost = analyze_solution(G, H, alpha, tour, pickups)

            if is_valid:
                total_cost = drive_cost + walk_cost
                print(f"  Valid solution! Total cost: {total_cost:.4f}")
                # Write the output
                write_ptp_solution_to_out(tour, pickups, input_file)
                print(f"  Output written to outputs/{input_file.replace('.in', '.out')}")
            else:
                print(f"  ERROR: Invalid solution!")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\nAll outputs generated!")


if __name__ == "__main__":
    main()
