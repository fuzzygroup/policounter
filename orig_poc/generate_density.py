import argparse
import matplotlib.pyplot as plt
from lwcc import LWCC

VALID_MODELS = ["CSRNet", "Bay", "DM-Count", "SFANet"]
VALID_WEIGHTS = ["SHA", "SHB", "QNRF"]


def main():
    parser = argparse.ArgumentParser(
        description="Generate density map from image using LWCC."
    )
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument(
        "-o",
        "--output",
        default="density_output.png",
        help="Output filename for the density image",
    )
    parser.add_argument(
        "--model_name",
        choices=VALID_MODELS,
        default="DM-Count",
        help="Model to use for counting",
    )
    parser.add_argument(
        "--model_weights",
        choices=VALID_WEIGHTS,
        default="SHA",
        help="Weights to use with the model",
    )

    args = parser.parse_args()

    # Run LWCC with specified model and weights
    count, density = LWCC.get_count(
        args.image_path,
        return_density=True,
        model_name=args.model_name,
        model_weights=args.model_weights,
        resize_img=False,
    )

    # Plot and save density map
    plt.imshow(density)
    plt.axis("off")
    plt.savefig(args.output, bbox_inches="tight", pad_inches=0)
    plt.close()

    print(f"Count: {count}")
    print(f"Density map saved to {args.output}")
    print(f"Model used: {args.model_name} with weights: {args.model_weights}")


if __name__ == "__main__":
    main()
