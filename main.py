import random as rand

from skimage import io
import matplotlib.pyplot as plt

from unit import Unit
import unit

# Set up the random seed to obtain repeatable results for debug
SEED = rand.randint(a=0, b=10000)
# SEED = 7352
print("seed: ", SEED, "\n")
rand.seed(SEED)

input_img = io.imread("input/unnamed.png")

adam = Unit()
lilith = Unit()
rei = adam.make_children_with(lilith)[0]

print(adam.fitness())
print(lilith.fitness())
print(rei.fitness())

def sortUnits(u:unit.Unit):
    return u.fitness_val

ITERATIONS = 1000
gen = [adam, lilith, rei]
for i in range(0, ITERATIONS):
    if(len(gen) < 2):
        break
    sample = sorted(rand.sample(gen, min(10, len(gen)-1)), key=sortUnits)

    best1 = sample[-1]
    best2 = sample[-2]
    parents = [best1, best2]
    if(len(gen) > 100):
        gen = list(filter(sample[0].__ne__, gen))
        gen = list(filter(sample[1].__ne__, gen))
        gen = list(filter(sample[2].__ne__, gen))

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

print(best.fitness(verbose=True))

img1 = best.draw_unit_on(unit.BLANK_IMAGE)
img2 = best.draw_unit_on(unit.TARGET_IMAGE)

plt.subplot(2, 1, 1)
plt.imshow(img1)
plt.subplot(2, 1, 2)
plt.imshow(img2)
plt.show()
plt.savefig("output/"+str(SEED)+".png")