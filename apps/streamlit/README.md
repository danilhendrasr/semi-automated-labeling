# Code Structure

## Directory Structure

```
streamlit
 ├─ function
 |   ├─ __init__.py
 |   |
 |   ├─ function_a
 |   |   ├─ __init__.py        
 |   |   ├─ sub_function_a_1.py
 |   |   └─ sub_function_a_2.py
 |   |
 |   └─ function_b
 |       ├─ __init__.py        
 |       └─ sub_function_b_1
 |           ├─ __init__.py
 |           └─ sub_function_b_1_1.py
 |           └─ sub_function_b_1_2.py
 |
 ├─ section
 |   ├─ __init__.py
 |   ├─ section_a.py
 |   └─ section_b.py
 |
 ├─ page
 |   ├─ __init__.py
 |   ├─ page_1.py
 |   ├─ page_2.py
 |   └─ page_3.py
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

## function

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