> [!NOTE]
> Visit [wiki.ros.org/urdf/XML](https://wiki.ros.org/urdf/XML) for official documentation on the URDF specification
# Creating link frames
A joint defines the transform between a parent link and child link. Thus, each link frame is located **at a joint** (aside from the base frame). Create coordinate frames for each link in the model using reference axes and planes.
![300](https://abedgnu.github.io/Notes-ROS/_images/joint.png)
# Creating collision primitives
All primitives must be constructed such that the origin frame of the part is located in the geometric center (i.e., use mid-plane extrusions). Configure all collision geometries as [envelope components](https://help.solidworks.com/2025/english/SolidWorks/sldworks/c_Assembly_Envelopes.htm) inside assemblies.
### Box
To easily generate the dimensions for a collision box on a link, hide the undesired parts and create a bounding box with `Insert` $\to$ `Reference Geometry` $\to$ `Bounding Box`. Note the dimensions and replicate the box as a separate part. Then, use width mates to center the box on the link.
### Cylinder
Ensure the Z axis lies along the height of the cylinder. Lock rotation if mating concentrically.
# Finding inertial components
0. Override mass properties of parts/entire link if volume-based calculation is not desired
1. Hide all irrelevant parts
2. `Evaluate` $\to$ `Mass Properties`
	- Uncheck *Include hidden bodies/components*
	- *Report coordinate values relative to* **the link frame**
3. Record the *Center of mass*, this is the xyz offset to apply in the `<inertial>` origin. No rotation will be applied as the moments will be reported aligned to the link frame.
4. Record the *Taken at the center of mass and aligned with the output coordinate system* values, these will be the `<inertia>` values

> [!IMPORTANT]
> The default values reported by SolidWorks use a positive tensor notation. [URDF assumes a negative product of inertia convention](https://wiki.ros.org/urdf/XML/link#:~:text=URDF%20assumes%20a%20negative%20product%20of%20inertia%20convention). Before inserting the inertia values into the URDF change the setting to *Negative Tensor Notation* in the *Options* of the Mass Properties panel.
# Exporting visual meshes
> [!TIP]
> For assemblies that contain multiple links, use [Display States](https://help.solidworks.com/2025/english/solidworks/sldworks/c_Display_States_in_Assemblies.htm) to easily separate visual groups.
### Single-color links
Each link is exported as an STL. Configure the export settings as:
- Set *Output Coordinate System* to the respective link frame
- Set *Unit* to `Meters`
- Set *Resolution* to `Coarse`
- Check *Do not translate STL output data to a positive space* 
- Check *Save all components of an assembly in a single file*

Since STL is purely geometric, the materials must be defined in the URDF.
### Multicolor links
Each link is exported as a STEP AP214. Configure the export settings as:
- Set *Output Coordinate System* to the respective link frame
- Check *Export appearances*

Run `meshify.py` on a STEP file or directory of STEP files to generate the associating GLB, DAE, and OBJ meshes.

> [!NOTE]
> [MuJoCo does not support textured meshes very well](https://github.com/google-deepmind/mujoco/issues/2672). The only approach is to split meshes by material and load each as a separate `<geom>`. For this reason, the OBJ exports are purely geometric, and do not generate a `.mtl` file.

