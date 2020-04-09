from skimage import data, io, draw
import matplotlib.pyplot as plt
import numpy as np
import random as rand
import unit

# Set up the randint seed to obtain repeatable results for debug
seed = rand.randint(a=0,b=10000)
# seed = 9621
print("seed: ", seed,"\n")
rand.seed(seed)
        
input_img = io.imread("input/unnamed.png")
# print(len(input_img[0]))

adam = unit.Unit(image = input_img)
lilith = unit.Unit(image = input_img)
rei = adam.make_children_with(lilith)[0]

img1 = adam.draw_unit_on(input_img)
img2 = lilith.draw_unit_on(input_img)
img3 = rei.draw_unit_on(input_img)

print(adam.fitness())
print(lilith.fitness())
print(rei.fitness())

gen = [adam,lilith,rei]
for i in range(0,1000):
    parents = rand.sample(gen,2)
    children = parents[0].make_children_with(parents[1])
    for child in children:
        child.mutate()
    gen += children

best = None
best_fitness = 0
for item in gen:
    print(item.fitness())
    if (best is None) or (item.fitness() < best_fitness):
        best = item
        best_fitness = item.fitness()

img4 = best.draw_unit_on(input_img)

plt.subplot(2,2,1)
plt.imshow(img1)
plt.subplot(2,2,2)
plt.imshow(img2)
plt.subplot(2,2,3)
plt.imshow(img3)
plt.subplot(2,2,4)
plt.imshow(img4)
plt.show()