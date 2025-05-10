import xml.etree.ElementTree as ET


def filter_toys(input_file, output_file, age=None, min_price=None, max_price=None):
    # Parse the input XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Create a new root element for the output
    new_root = ET.Element("toys")

    # Iterate through toys in the input file
    for toy in root.findall('./toy'):
        toy_age = toy.find('age_category').text
        toy_price = float(toy.find('price').text)

        # Check if the toy meets the criteria
        meets_age_criteria = True if age is None else age in toy_age
        meets_min_price = True if min_price is None else toy_price >= min_price
        meets_max_price = True if max_price is None else toy_price <= max_price

        if meets_age_criteria and meets_min_price and meets_max_price:
            # Add the toy to the new XML
            new_root.append(toy)

    # Create a new tree and write to the output file
    new_tree = ET.ElementTree(new_root)
    new_tree.write(output_file, encoding='utf-8', xml_declaration=True)


filter_toys('toys.xml', 'filtered_toys.xml', age='3+', max_price=500)