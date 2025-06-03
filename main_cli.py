from nlp_processor import NLPProcessor
from r_interface import RInterface
import os

def main():
    """
    Main function to run the Natural Language to Plot CLI.
    """
    print("Welcome to the Natural Language to Plot CLI!")
    print("-----------------------------------------------")
    print("This tool allows you to describe a plot in natural language,")
    print("and it will attempt to generate it using R's ggplot2.")
    print("\nTo use:")
    print("1. Ensure you have R installed and Rserve running.")
    print("   In R, run: library(Rserve); Rserve(args='--no-save')")
    print("2. When prompted, describe the plot you want.")
    print("   Example: 'Create a scatter plot of Sepal.Length vs Petal.Width from the iris dataset, color by Species. Title: Iris Flowers'")
    print("3. Type 'exit' or 'quit' to close the CLI.")
    print("-----------------------------------------------\n")

    nlp_processor = None
    r_interface = None

    try:
        print("Initializing NLP Processor...")
        nlp_processor = NLPProcessor()
        print("NLP Processor initialized.")

        print("\nInitializing R Interface and connecting to Rserve...")
        r_interface = RInterface()
        print("R Interface initialized and connected to Rserve.")

        while True:
            try:
                user_input = input("\nDescribe the plot you want to create (or type 'exit'/'quit'): \n> ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting CLI...")
                    break

                if not user_input.strip():
                    print("Please enter a description.")
                    continue

                print("\nParsing your description...")
                plot_spec = nlp_processor.parse_description(user_input)

                if not plot_spec or not plot_spec.get("plot_type"):
                    print("Could not fully understand the plot description or determine the plot type. Please try rephrasing.")
                    print(f"Parsed spec was: {plot_spec}")
                    continue

                print(f"Understood plot specification: {plot_spec}")

                output_filename = "output_plot.png"
                print(f"Attempting to generate plot as '{output_filename}'...")

                # Ensure plot_spec components are not None where critical
                if not plot_spec.get('x_variable'):
                    print("Error: X-variable could not be determined from the description. Cannot generate plot.")
                    continue


                generated_file_path = r_interface.generate_plot(plot_spec, output_filename)

                if generated_file_path and os.path.exists(generated_file_path):
                    print(f"\nSuccessfully generated plot: {generated_file_path}")
                    print(f"You can open '{generated_file_path}' to view the plot.")
                else:
                    print("\nPlot generation seemed to complete, but the output file was not found.")

            except Exception as e:
                print(f"\nAn error occurred during processing: {e}")
                # Optionally, you could add more specific error handling here
                # for NLP or RInterface specific exceptions if they are defined.

    except ConnectionRefusedError:
        print("\nCRITICAL ERROR: Could not connect to Rserve.")
        print("Please ensure Rserve is running. In R: library(Rserve); Rserve(args='--no-save')")
    except Exception as e:
        print(f"\nA critical error occurred during initialization or shutdown: {e}")
    finally:
        if r_interface:
            print("\nClosing Rserve connection...")
            r_interface.close()
        print("CLI finished.")

if __name__ == "__main__":
    main()
