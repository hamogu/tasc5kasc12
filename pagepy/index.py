from glob import glob

def data(**kwargs):
    images = glob('images/slide-*')
    images.sort()

    return {'images': images}
