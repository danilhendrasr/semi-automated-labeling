import section

def dataset_preprocessing():
    section.preprocessing('temp', ['None', 'grayscale', 'resize', 'scale'], section_key='preprocessing - 1')
    section.preprocessing('temp', ['None', 'grayscale'], section_key='preprocessing - 2')