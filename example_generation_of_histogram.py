from ss_overlay import *
import matplotlib.pyplot as plt

# specify file names (run from same directory)
pdb_file = "akt1_1unq_PM_modeller.B99990001.pdb"
data_file = "Contacts_protein-POP3_full_ALL.dat"
stride_output_file = "akt1_1unq.stride"

# import data for histogram
data_lines = open("Contacts_protein-POP3_full_ALL.dat").read().splitlines()
residues = []
contacts = []
for x in range(0, len(data_lines)):
    residues.append(int(data_lines[x].split(" ")[0]))
    contacts.append(float(data_lines[x].split(" ")[2]))

# uncomment line below if you want to test usage of stride to generate stride ss file, otheriwse already generated file will be used
#generate_stride_ss_file(pdb_file,stride_output_file)

# call secondary_structure_assignment function to read stride file and interpret secondary structure
secondary_structure = read_secondary_structure_assignment(stride_output_file)

# set up and generate plot
fig, ax = plt.subplots()
plt.figsize = (7,5)
ax.bar(residues, contacts)
ax.margins(x=0, y=0)

# *** GENERATE SECONDARY STRUCTURE OVERLAY ***
# create a secondary_structure_overlay object, providing it with the ax object, the residue numbers and the secondary structure
# it will automatically generate the overlay upon creation
generate_patches = secondary_structure_overlay(ax,residues,secondary_structure)

# finalise and save plot
ax.set_title('Example protein histogram with ss overlay', pad=40)
plt.xlabel("Residue")
ylabel = plt.ylabel('Normalised frequency of contacts')
#ylabel.set_rotation(0)
plt.tight_layout()
plt.savefig("example_figure.png",dpi=200)
print("Saved example_figure.png.")