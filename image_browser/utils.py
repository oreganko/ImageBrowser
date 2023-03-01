def get_image_name(name):
    return name if len(name) <= 50 else '...' + name[len(name) - 47:]
