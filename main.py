"""Main module of program"""
import random as rand

from skimage import io
import matplotlib.pyplot as plt

from unit import Unit
import unit
import constants
import preprocessing

# Set up the random seed to obtain repeatable results for debug
SEED = rand.randint(a=0, b=10000)
# SEED = 7352
print("seed: ", SEED, "\n")
rand.seed(SEED)

# Read image
TARGET_IMAGE = preprocessing.rgba2rgb(io.imread(constants.INPUT_IMG_NAME))
# Create canvas
BLANK_IMAGE = preprocessing.get_blank(
    preprocessing.get_dominant_color(TARGET_IMAGE))
# Setup unit class
Unit.setup_conditions(TARGET_IMAGE, BLANK_IMAGE)

adam = Unit()
lilith = Unit()
rei = adam.make_children_with(lilith)[0]

print(adam.fitness())
print(lilith.fitness())
print(rei.fitness())


def sortUnits(u: unit.Unit):
    return u.fitness_val


gen = [adam, lilith, rei]
for i in range(0, constants.ITERATIONS):
    if(len(gen) < 2):
        break
    sample = sorted(rand.sample(gen, min(10, len(gen)-1)), key=sortUnits)

    best1 = sample[-1]
    best2 = sample[-2]
    parents = [best1, best2]
    rem = list(sample[-1:-2])
    gen = [i for i in gen if i not in rem]

    children = parents[0].make_children_with(parents[1])
    for child in children:
        mutant = child.mutate()
        gen.append(mutant)

best = None
best_fitness = 0
for item in gen:
    if (best is None) or (item.fitness_val > best_fitness):
        best = item
        best_fitness = item.fitness_val

constants.VERBOSE_MODE = True
print(best.fitness())
constants.VERBOSE_MODE = False


img1 = best.draw_unit_on(BLANK_IMAGE)
img2 = TARGET_IMAGE

dpi = 80
plt.gcf().set_size_inches(1024/dpi, 512/dpi)
plt.subplot(1, 2, 1)
plt.imshow(img1)
plt.subplot(1, 2, 2)
plt.imshow(img2)
# plt.show()
plt.savefig("output/"+str(constants.ITERATIONS)+"x"+str(SEED)+".png")
