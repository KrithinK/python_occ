a = [1, 2, 3]
a.append(4)
print(a)
print(len(a))

print(bcolors.OKBLUE + "This is the arroach direction of block " +
              str(i) + bcolors.ENDC)
        bb1 = get_boundingbox(sub_assemblies[i])
        bb = get_boundingbox(temp)
        pos_posy = Process(target=positive_y, args=(
            bb1, bb, temp, sub_assemblies[i]))
        pos_negy = Process(target=negative_y, args=(
            bb1, bb, temp, sub_assemblies[i]))
        pos_posx = Process(target=positive_x, args=(
            bb1, bb, temp, sub_assemblies[i]))
        pos_negx = Process(target=negative_x, args=(
            bb1, bb, temp, sub_assemblies[i]))
        pos_posz = Process(target=positive_z, args=(
            bb1, bb, temp, sub_assemblies[i]))
        pos_negz = Process(target=negative_z, args=(
            bb1, bb, temp, sub_assemblies[i]))

        pos_posy.start()
        pos_negy.start()
        pos_posx.start()
        pos_negx.start()
        pos_posz.start()
        pos_negz.start()

        pos_posy.join()
        pos_negy.join()
        pos_posx.join()
        pos_negx.join()
        pos_posz.join()
        pos_negz.join()

        temp = BRepAlgoAPI_Fuse(
            temp, sub_assemblies[i]).Shape()
