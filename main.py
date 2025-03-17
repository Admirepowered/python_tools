import coredumpy
def main():
    print(__name__)


if __name__ =='__main__':
    main()
    coredumpy.patch_except(directory='./dumps')
    coredumpy.patch_unittest(directory='./dumps')
    0/0