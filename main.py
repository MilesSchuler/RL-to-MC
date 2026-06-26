from converter import ModelConverter


def main():
    converter = ModelConverter()
    converter.convert("BigBen", target_height=12, subresolution=8)


if __name__ == "__main__":
    main()