import argparse
import os
import glob
import shutil
import matplotlib.pyplot as plt
from lwcc import LWCC

VALID_MODELS = ["CSRNet", "Bay", "DM-Count", "SFANet"]
VALID_WEIGHTS = ["SHA", "SHB", "QNRF"]

def is_image_file(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))

def generate_density_map(image_path, density_path, model_name, model_weights):
    count, density = LWCC.get_count(
        image_path,
        return_density=True,
        model_name=model_name,
        model_weights=model_weights,
        resize_img=False
    )
    plt.imshow(density)
    plt.axis('off')
    plt.savefig(density_path, bbox_inches='tight', pad_inches=0)
    plt.close()
    return count

def main():
    parser = argparse.ArgumentParser(description="Batch density-map + HTML generation with LWCC.")
    parser.add_argument("input_dir", help="Directory containing input images")
    parser.add_argument("-o", "--output_dir", default="output", help="Where to drop maps & HTML")
    parser.add_argument("--model_name", choices=VALID_MODELS, default="DM-Count", help="Model to use")
    parser.add_argument("--model_weights", choices=VALID_WEIGHTS, default="SHA", help="Weights to use")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    image_files = [p for p in glob.glob(os.path.join(args.input_dir, "*")) if is_image_file(p)]
    results = []

    for image_path in image_files:
        fname = os.path.basename(image_path)
        # copy original into output_dir so HTML can load it by simple filename
        dest_orig = os.path.join(args.output_dir, fname)
        shutil.copy(image_path, dest_orig)

        density_name = f"density_{fname}"
        density_path = os.path.join(args.output_dir, density_name)
        count = generate_density_map(dest_orig, density_path, args.model_name, args.model_weights)

        results.append((fname, density_name, count))

    # write out HTML
    html_path = os.path.join(args.output_dir, "index.html")
    with open(html_path, "w") as f:
        f.write("<!doctype html>\n<html><head><meta charset='utf-8'>\n")
        f.write("<title>LWCC Results</title></head><body>\n<h1>Density Map Results</h1>\n")
        for orig, dens, cnt in results:
            f.write(f"<div style='margin-bottom:2em;'>\n")
            f.write(f"  <h2>{orig} — Count: {cnt}</h2>\n")
            f.write(f"  <img src='{orig}' alt='original' style='width:45%; margin-right:5%;'>\n")
            f.write(f"  <img src='{dens}' alt='density map' style='width:45%;'>\n")
            f.write("</div>\n")
        f.write("</body></html>")

    print(f"✅ Done! Check out {html_path}")

if __name__ == "__main__":
    main()

