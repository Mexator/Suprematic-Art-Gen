"""Main module of program"""
import random as rand
import time

from skimage import io, transform
import matplotlib.pyplot as plt

from unit import Unit
import unit
import constants
import preprocessing
import fitness_helper_functions as fit

# Set up the random seed to obtain repeatable results for debug
if constants.SEED is None:
    constants.SEED = int(time.time())
print("seed: ", constants.SEED, "\n")
rand.seed(constants.SEED)

print("Input reading and preprocessing: Starting")
launch_time = time.time()

# Read image
TARGET_IMAGE = preprocessing.rgba2rgb(io.imread(constants.INPUT_IMG_NAME))
# Create canvas
BLANK_IMAGE = preprocessing.get_blank(
    preprocessing.get_dominant_color(TARGET_IMAGE))

# Setup fitness function parameters
fit.setup_fitness_parameters(TARGET_IMAGE, BLANK_IMAGE[0][0])

print("Input reading and preprocessing: Done in",
      time.time() - launch_time, "sec")

print("Creating initial generation: Starting")
gen_start = time.time()

GENERATION = [Unit() for _ in range(constants.START_UNITS)]

print("Creating initial generation: Done in",
      time.time() - gen_start, "sec")

print("Starting evolutionary loop", f"({constants.ITERATIONS} iterations)")
one_percent = max(int(constants.ITERATIONS / 100),1)

for i in range(0, constants.ITERATIONS):

    if i % one_percent == 0 and constants.VERBOSE_MODE:
        print(f"{i / one_percent}%")

    # If only one unit left - break
    if len(GENERATION) < 2:
        break

    # Choose 10 random units, then 2 best of them
    sample = sorted(rand.sample(GENERATION, min(10, len(GENERATION))),
                    key=unit.unit_comparator_metric)

    best1 = sample[-1]
    best2 = sample[-2]
    parents = [best1, best2]
    rem = list(sample[-2:-1])
    GENERATION = [i for i in GENERATION if i not in rem]
    children = parents[0].make_children_with(parents[1])
    
    to_be_removed = [best1,best2] + children
    to_be_removed = sorted(to_be_removed, key = unit.unit_comparator_metric)

    GENERATION = [item for item in GENERATION if item not in to_be_removed]
    GENERATION += to_be_removed[-3: -1]
BEST = None
BEST_FITNESS = 0
for item in GENERATION:
    if (BEST is None) or (item.fitness_val > BEST_FITNESS):
        BEST = item
        BEST_FITNESS = item.fitness_val

print(BEST.fitness(verbose=True))

DPI = 80
drawn = BEST.draw_unit_on(BLANK_IMAGE, scale=2)
drawn = transform.resize(drawn,(512,512), anti_aliasing=True)

plt.gcf().set_size_inches(2048/DPI, 1024/DPI)
plt.subplot(1, 2, 1)
plt.imshow(drawn)
plt.subplot(1, 2, 2)
plt.imshow(TARGET_IMAGE)
plt.savefig("output/combined/"+str(constants.ITERATIONS)+"x"+str(constants.SEED)+".png")


io.imsave("output/"+str(constants.ITERATIONS)+"x"+str(constants.SEED)+".png",drawn)
if constants.SHOW_RESULT:
    plt.show()
