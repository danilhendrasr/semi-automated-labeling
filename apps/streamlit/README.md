# Code Structure

## Directory Structure

```
streamlit
 ├─ function
 |   ├─ __init__.py
 |   |
 |   ├─ function_name_1
 |   |   ├─ __init__.py        
 |   |   ├─ function_name_1_sub_1.py
 |   |   └─ function_name_1_sub_1.py
 |   |
 |   └─ function_name_2
 |       ├─ __init__.py        
 |       └─ function_name_2_sub_1
 |           ├─ __init__.py
 |           └─ function_name_2_sub_1_sub_1.py
 |           └─ function_name_2_sub_1_sub_2.py
 |
 ├─ section
 |   ├─ __init__.py
 |   ├─ section_name_1.py
 |   └─ section_name_2.py
 |
 ├─ page
 |   ├─ __init__.py
 |   ├─ page_name_1.py
 |   └─ page_name_2.py
 |   
 └─ main.py
```

## Definition

- `main.py` : Main program which wraps all page.

- `page` : Part of a program that represent a whole page, which may contains several sections.

- `section` : Part of a page which may contains several functions.

- `function` : Features or logics to process the application.

## Migrating from old code structure to new code structure

```
main.py    =====>   page + section
utils.py   =====>   function
```

## Page

### `page/__init__.py`
```py
from .page_name_1 import page_name_1
from .page_name_2 import page_name_2
```

### `page/page_name_1.py`
```py
import streamlit as st
import section
def page_name_1(page_key):
    st.header('page_name_1')
    section.section_name_1(section_key=f'{page_key} section_name_1')
    section.section_name_2(section_key=f'{page_key} section_name_2 - 1')
    section.section_name_2(section_key=f'{page_key} section_name_2 - 2')
```

## Section

### `section/__init__.py`
```py
from .section_name_1 import section_name_1
from .section_name_2 import section_name_2
```

### `section/section_name_1.py`
```py
import streamlit as st
import function
def section_name_1(section_key):
    st.subheader('section_name_1')
    process = st.button('Process', key=f'{section_key} process button')
    if process: function.function_name_1(function_key =f'{section_key} function_name_1')
```

## Function

### `function/__init__.py`
```py
from .function_name_1 import function_name_1
from .function_name_2 import function_name_2
```

### `function/function_name_1.py`
```py
import streamlit as st
def function_name_1(function_key):
    pass
```
If the function doesn't contain any `streamlit` functionality, it'll be okay to not include `function_key` in the parameters.
```py
def function_name_1():
    pass
```

## Coding Style Convention

- All file (package, module, program) must be written in `lower_snake_case`.
- All class must be written in `UpperCamelCase`.

For more information about writing convention, read [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/).

---

This project was developed as part of Nodeflux Internship x Kampus Merdeka.
