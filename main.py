import random as rand

from skimage import io
import matplotlib.pyplot as plt

from unit import Unit

# Set up the randint seed to obtain repeatable results for debug
seed = rand.randint(a=0, b=10000)
# seed = 9621
print("seed: ", seed, "\n")
rand.seed(seed)

input_img = io.imread("input/unnamed.png")
# print(len(input_img[0]))

adam = Unit(image=input_img)
lilith = Unit(image=input_img)
rei = adam.make_children_with(lilith)[0]

img1 = adam.draw_unit_on(input_img)
img2 = lilith.draw_unit_on(input_img)
img3 = rei.draw_unit_on(input_img)

print(adam.fitness())
print(lilith.fitness())
print(rei.fitness())


gen = [adam, lilith, rei]
for i in range(0, 1000):
    if(len(gen)<2):
        break
    sample = rand.sample(gen, min(10, len(gen)-1))
    best1 = sample[0]
    best2 = sample[1]
    for i in range(2,len(sample)):
        if (sample[i].fitness_val > best1.fitness_val):
            best1 = sample[i]
        elif (sample[i].fitness_val > best2.fitness_val):
            best2 = sample[i]
    parents = [best1,best2]

    children = parents[0].make_children_with(parents[1])
    for child in children:
        child.mutate()
    gen += children
    for item in gen:
        if item.age > Unit.lifecycle:
            gen.remove(item)
        item.age += 1

best = None
best_fitness = 0
for item in gen:
    if (best is None) or (item.fitness() > best_fitness):
        best = item
        best_fitness = item.fitness()

img4 = best.draw_unit_on(input_img)
print(best_fitness)

plt.subplot(2, 2, 1)
plt.imshow(img1)
plt.subplot(2, 2, 2)
plt.imshow(img2)
plt.subplot(2, 2, 3)
plt.imshow(img3)
plt.subplot(2, 2, 4)
plt.imshow(img4)
plt.show()
