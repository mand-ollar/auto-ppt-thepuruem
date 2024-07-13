"""Select an option among multiple options"""


def select_option(
    options: list[str],
    description: str,
) -> int:
    """With a list of options, output the selected option index"""

    print("\n*** SELECT OPTION HELPER ***\n")
    print(f">> {description} <<")
    print()

    for i, option in enumerate(options):
        print(f"  [{i}] {option}")

    selected_idx_string = input("\nSelect option: ")

    while True:
        try:
            selected_idx_int = int(selected_idx_string)
            selected_option = options[selected_idx_int]
            print(f"\nYou selected {selected_option}!\n")
            break

        except ValueError:
            print("Invalid input. Please enter a number.")
            selected_idx_string = input("\nSelect option: ")

        except IndexError:
            print("Invalid input. Please enter a valid number.")
            selected_idx_string = input("\nSelect option: ")

    return selected_idx_int
