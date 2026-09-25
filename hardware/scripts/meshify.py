import cascadio
import trimesh
import tyro
from pathlib import Path
from typing import Annotated
from collections import defaultdict


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{int(size_bytes)}B"
    
    for unit in ["KB", "MB"]:
        size_bytes /= 1024
        if size_bytes < 1024 or unit == "MB":
            return f"{size_bytes:.1f}{unit}"


def export_objs_by_material(scene: trimesh.Scene, output_dir: Path, stem: str) -> None:
    """Export scene geometries as separate OBJ files grouped by material color."""
    groups = defaultdict(list)
    
    for geom in scene.dump():
        if hasattr(geom, 'visual') and hasattr(geom.visual, 'material'):
            key = tuple(geom.visual.material.main_color) if geom.visual.material else None
            groups[key].append(geom)
    
    for idx, meshes in enumerate(groups.values()):
        obj_path = output_dir / f"{stem}_{idx}.obj"
        trimesh.util.concatenate(meshes).export(obj_path, include_normals=True, include_texture=False)
        print(f"Created {obj_path} {format_size(obj_path.stat().st_size)}")


def convert_step(step_file: Path, output_dir: Path, split_obj: bool) -> None:
    """Convert STEP/STP file to GLB, OBJ, and DAE formats."""
    stem = step_file.stem
    
    glb_bytes = cascadio.load(data=step_file.read_bytes(), tol_linear=0.1, tol_angular=1)
    scene = trimesh.load(trimesh.util.wrap_as_stream(glb_bytes), file_type="glb")

    glb_path = output_dir / f"{stem}.glb"
    scene.export(glb_path)
    print(f"Created {glb_path} {format_size(glb_path.stat().st_size)}")
    
    if split_obj:
        export_objs_by_material(scene, output_dir, stem)
    else:
        obj_path = output_dir / f"{stem}.obj"
        scene.export(obj_path, mtl_name=f"{stem}.mtl", include_normals=True)
        print(f"Created {obj_path} {format_size(obj_path.stat().st_size)}")

    dae_bytes = trimesh.exchange.dae.export_collada(scene.dump())
    dae_path = output_dir / f"{stem}.dae"
    dae_path.write_bytes(dae_bytes)
    print(f"Created {dae_path} {format_size(dae_path.stat().st_size)}")


def main(
    file: Path,
    /,
    output: Annotated[Path, tyro.conf.arg(aliases=["-o"], metavar="DIR")] = Path("assets"),
    split_obj: tyro.conf.FlagCreatePairsOff[bool] = False,
) -> None:
    """Convert STEP files to GLB, OBJ, and DAE formats.

    Args:
        file: Path to input STEP file or directory of STEP files
        output: Path to output directory for converted files
        split_obj: Export multiple OBJ files grouped by material
    """
    if not file.exists():
        raise FileNotFoundError(f"Path not found: {file}")
    
    output.mkdir(parents=True, exist_ok=True)
    
    SUFFIXES = {".step", ".stp"}
    if file.is_dir():
        files = [f for f in file.iterdir() if f.suffix.lower() in SUFFIXES]
        if not files:
            raise ValueError(f"No STEP files found in: {file}")
    elif file.suffix.lower() in SUFFIXES:
        files = [file]
    else:
         raise ValueError(f"Unsupported file format: {file.suffix}")
    
    for f in files:
        convert_step(f, output, split_obj)


if __name__ == "__main__":
    tyro.cli(main)