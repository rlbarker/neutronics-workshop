import openmc
import matplotlib.pyplot as plt

# MATERIALS

# creates a single material
mats = openmc.Materials()
 
shielding_material = openmc.Material(name="breeder") 
shielding_material.add_nuclide('Fe56', 1, percent_type='ao')
shielding_material.set_density('g/cm3', 7)

mats = [shielding_material]



# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=200, boundary_type='vacuum')

# cells
shield_cell = openmc.Cell(region=-sph1)
shield_cell.fill = shielding_material

universe = openmc.Universe(cells=[shield_cell])

geom = openmc.Geometry(universe)

# Create mesh which will be used for tally and weight window
my_ww_mesh = openmc.RegularMesh()
mesh_height = 10  # number of mesh elements in the Y direction
mesh_width = 10  # number of mesh elements in the X direction
my_ww_mesh.dimension = [mesh_width, 1, mesh_height] # only 1 cell in the Y dimension
my_ww_mesh.lower_left = [-100, -100, -100]  # physical limits (corners) of the mesh
my_ww_mesh.upper_right = [100, 100, 100]




lower_ww_bounds=[]
upper_ww_bounds=[]
for mesh_element in range(1,  (mesh_height * mesh_width)+1):
    if mesh_element > (mesh_height * mesh_width) *0.5:
        lower_ww_bounds.append(0.001)
        upper_ww_bounds.append(0.7)
    else:
        lower_ww_bounds.append(-1)
        upper_ww_bounds.append(-1)


# docs on ww https://docs.openmc.org/en/latest/_modules/openmc/weight_windows.html?highlight=weight%20windows
ww = openmc.WeightWindows(
    mesh =my_ww_mesh,
    upper_ww_bounds=upper_ww_bounds,
    lower_ww_bounds=lower_ww_bounds,
    particle_type='neutron',
    energy_bins=(0.0, 100_000_000.0),  # applies this weight window to neutrons of within a large energy range (basically all neutrons in the simulation)
    survival_ratio=5
)


# creates a 14MeV point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])

# SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
sett.batches = 100
sett.inactive = 0
sett.particles = 500
sett.source = source
sett.run_mode = 'fixed source'
sett.weight_windows = ww


# Create mesh which will be used for tally and weight window
my_tally_mesh = openmc.RegularMesh()
my_tally_mesh.dimension = [mesh_width, 1, mesh_height]  # only 1 cell in the Y dimension
my_tally_mesh.lower_left = [-100, -100, -100]   # physical limits (corners) of the mesh
my_tally_mesh.upper_right = [100, 100, 100]



tallies = openmc.Tallies()
# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(my_tally_mesh)
mesh_tally = openmc.Tally(name='flux_on_mesh')
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ['flux']
tallies.append(mesh_tally)

# combines the geometry, materials, settings and tallies to create a neutronics model
model = openmc.model.Model(geom, mats, sett, tallies)

# plt.show(universe.plot(width=(180, 180), basis='xz'))

# # deletes old files
# !rm summary.h5
# !rm statepoint.*.h5

# runs the simulation
output_filename = model.run()

# open the results file
results = openmc.StatePoint(output_filename)

# access the flux tally
my_tally = results.get_tally(scores=['flux'])
my_slice = my_tally.get_slice(scores=['flux'])
my_slice.mean.shape = (mesh_width, mesh_height)
fig = plt.subplot()

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
fig.imshow(my_slice.mean, extent=[-200,200,-200,200], vmin=1e-5, vmax=28)
plt.show()

fig.imshow(my_slice.std_dev, extent=[-200,200,-200,200])#, vmin=1e-7, vmax=1)

# np.amax(my_slice.mean)
28

plt.show()

# notice that neutrons are produced and emitted isotropically from a point source.
# There is a slight increase in flux within the neutron multiplier.
