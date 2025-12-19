"""
Course: Scientific virtualisation and virtual reality
Names: Tika van Bennekum, Anezka Potesilova
Student 13392425, 15884392

File description:
    This is the main file.
    Here we create a dynamic visualization of a wildfire using VTK.
"""

#!/usr/bin/env vtkpython
from multiview import create_multiview_visualisation
from singleview import create_singleview_visualisation


def prompt_user_settings():
    """
    Interactive menu to prompt user for visualization mode and animation type.
      - mode: "single" or "multi"
      - animation_type: "interactive" or "frames"
      - pterrain: "mountain" or "valley
    """
    print("\n" + "=" * 60)
    print("WILDFIRE VISUALIZATION - SETUP MENU")
    print("=" * 60)

    # mode
    print("\n1. Choose visualization mode:")
    print("   [1] Multi-view (six topographies compared side-by-side)")
    print("   [2] Single-view (one topography)")
    mode_choice = input("   Select (1 or 2): ").strip()

    if mode_choice == "2":
        mode = "single"
    else:
        mode = "multi"

    # animation type
    print("\n2. Choose animation type:")
    print("   [1] Interactive window (explore with mouse/keyboard)")
    print("   [2] Generate animation frames (PNG sequence)")
    anim_choice = input("   Select (1 or 2): ").strip()

    if anim_choice == "2":
        animation_type = "frames"
    else:
        animation_type = "interactive"

    # terrain
    params = {
        "terrain_type": "mountain",
        "fire_type": "head",
        "curvature": 80,
        "timestep": 10000,
        "timestep_start": 10000,
        "timestep_end": 15000,
    }

    if mode == "single":
        print("\n3. Configure single-view simulation:")
        print("   Terrain: [1] Mountain (default), [2] Valley")
        terrain_choice = input("   Select (1 or 2): ").strip()
        if terrain_choice == "2":
            params["terrain_type"] = "valley"

        if params["terrain_type"] == "mountain":
            print("   Fire position: [1] Head (default), [2] Back")
            fire_choice = input("   Select (1 or 2): ").strip()
            if fire_choice == "2":
                params["fire_type"] = "back"

            print("   Curvature: [1] 40 (default), [2] 80, [3] 320")
            curve_choice = input("   Select (1, 2, or 3): ").strip()
            if curve_choice == "1":
                params["curvature"] = 40
            elif curve_choice == "3":
                params["curvature"] = 320

        if animation_type == "interactive":
            print("\n   Enter timestep for interactive view:")
            try:
                timestep_input = int(
                    input("   Timestep (default 10000): ").strip() or "10000"
                )
                params["timestep"] = timestep_input
            except ValueError:
                print("   Invalid input. Using default 10000.")
                params["timestep"] = 10000
        elif animation_type == "frames":
            print("\n   Enter starting timesteps for animation frames:")
            try:
                start_input = int(
                    input("   Starting timestep (default 10000): ").strip() or "10000"
                )
                params["timestep_start"] = start_input
            except ValueError:
                print("   Invalid input. Using defaults 10000 to 15000.")
                params["timestep_start"] = 10000
    else:
        print("\n3. Configure multi-view simulation:")
        if animation_type == "interactive":
            print(
                "   Enter a single timestep to visualize all 6 simulations at that point:"
            )
            try:
                timestep_input = int(
                    input("   Timestep (default 10000): ").strip() or "10000"
                )
                params["timesteps"] = [timestep_input]
            except ValueError:
                print("   Invalid input. Using default 10000.")
                params["timesteps"] = [10000]
        else:
            print("   Enter starting and ending timesteps for animation frames:")
            try:
                start_input = int(
                    input("   Starting timestep (default 10000): ").strip() or "10000"
                )
                end_input = int(
                    input("   Ending timestep (default 15000): ").strip() or "15000"
                )
                if start_input > end_input:
                    start_input, end_input = end_input, start_input
                params["timestep_start"] = start_input
                params["timestep_end"] = end_input
                # For frames mode, we might generate multiple frames; store as range
                params["timesteps"] = [start_input, end_input]
            except ValueError:
                print("   Invalid input. Using defaults 10000 to 30000.")
                params["timestep_start"] = 10000
                params["timestep_end"] = 30000
                params["timesteps"] = [10000, 30000]

    print("\n" + "=" * 60)
    print(f"Mode: {mode.upper()}")
    print(f"Animation: {animation_type.upper()}")
    if mode == "single":
        print(f"Terrain: {params['terrain_type'].upper()}")
        if params["terrain_type"] == "mountain":
            print(f"Fire: {params['fire_type'].upper()}")
            print(f"Curvature: {params['curvature']}")
        if animation_type == "interactive":
            print(f"Timestep: {params['timestep']}")
        else:
            print(
                f"Timestep range: {params['timestep_start']} to {params['timestep_end']}"
            )
    else:
        if animation_type == "interactive":
            print(f"Timestep: {params['timesteps'][0]}")
        else:
            print(
                f"Timestep range: {params['timestep_start']} to {params['timestep_end']}"
            )
    print("=" * 60 + "\n")

    return mode, animation_type, params


if __name__ == "__main__":
    # prompt user for settings
    mode, animation_type, params = prompt_user_settings()

    if mode == "multi":
        create_multiview_visualisation(
            animation=(animation_type == "frames"),
            timestep_start=params["timestep_start"],
            timestep_end=params["timestep_end"],
        )
    else:
        create_singleview_visualisation(
            animation=(animation_type == "frames"),
            terrain_type=params["terrain_type"],
            fire_type=params["fire_type"],
            curvature=params["curvature"],
            timestep=params["timestep"],
        )
