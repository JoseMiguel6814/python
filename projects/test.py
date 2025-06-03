import dlib
print(dlib.DLIB_USE_CUDA)  # Debe imprimir "True"
print(dlib.cuda.get_num_devices())  # Debe mostrar tu GPU (ej: 1)