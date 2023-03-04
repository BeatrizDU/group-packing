import json
import pandas as pd

# Define variables order for JSON construction
# =============================================================================
group_order = ["treatment", "age", "gender",
               "tech_company", "benefits", "country"]
# =============================================================================

class PrepareData():
    def __init__(self, frame: str) -> None:
        self.frame = frame

    def get_method(self):
        method_name = f"prepare_{self.frame}"
        method = getattr(self, method_name, "prepare_invalid_frame")
        return method

    def prepare_country(self, country: str):
        return country

    def prepare_treatment(self, treatment: str):
        return f"treatment = {treatment}"

    def prepare_age(self, age: int):
        return age

    def prepare_gender(self, gender: str):
        return f"gender = {gender}"

    def prepare_benefits(self, benefits: str):
        return f"benefits = {benefits}"

    def prepare_tech_company(self, tech_company: str):
        return f"tech_company = {tech_company}"

def get_children_list(children_dict: dict):
    return children_dict["children"]

def get_element_dict(element: str) -> dict:
    return {"name": element, "children": []}

df = pd.read_csv("dataset_mental_health_survey.csv", usecols=group_order)

# Dataset preparation
# =============================================================================
for frame_label in group_order:
    temp_object = PrepareData(frame_label)
    prepare_data = temp_object.get_method()
    df[frame_label] = df[frame_label].apply(prepare_data)

if "age" in df.columns:
    # Age needs a different approach to classify it into ranges
    # Define the bins and labels for classification
    bins = [df["age"].min(), 17, 24, 34, 44, 54, 64, df["age"].max()]
    labels = ["Under 18", "18-24", "25-34",
              "35-44", "45-54", "55-64", "65 and over"]

    # Use pandas.cut() function to classify the values in column 'age' into the defined bins
    df['age'] = pd.cut(df['age'], bins=bins, labels=labels)
# =============================================================================

#Group columns following group_order
# =============================================================================
groups = df.groupby(group_order)
groups_count = groups[(group_order[-1])].count()
# =============================================================================

# Create a dictionary of each group
# =============================================================================
output_dict = groups_count.to_dict()
groups_dict = {}
index = 0
for key in output_dict:
    key_str = str(key)
    value = output_dict[key]
    if value != 0:
        temp_dict = {}
        for i in range(len(group_order)):
            temp_dict.update({group_order[i]: key[i]})
        temp_dict.update({"count_value": value})
        groups_dict.update({index: temp_dict})
        index += 1
# =============================================================================

# Children dictionary creation
# =============================================================================
json_dict = {"name": "Flare", "children": []}
count_value_dict = {}
last_label = group_order[-1]
labels_number = len(group_order)

for i in groups_dict:
    temp_children = {}
    childrens = get_children_list(json_dict)
    prev_children_index = 0
    for index in range(labels_number):
        label = group_order[index]
        elem = groups_dict[i][label]
        if label == last_label:
            group_value = groups_dict[i]["count_value"]
            count_value_dict = {"name": elem, "value": group_value}
            childrens.append(count_value_dict)
            break

        if not childrens:
            childrens.append(get_element_dict(elem))

        elem_needed_flag = True
        children_number = len(childrens)
        for children_index in range(children_number):
            children_dict = childrens[children_index]
            name_of_children = children_dict["name"]
            if name_of_children == elem:
                childrens = get_children_list(children_dict)
                elem_needed_flag = False

        if elem_needed_flag:
            childrens.append(get_element_dict(elem))
            childrens = get_children_list(childrens[children_number])
# =============================================================================        

# Export dictionary to JSON
# =============================================================================
json_data = json.dumps(json_dict, indent=2)
json_file = open("data.json", "w")
json_file.write(json_data)
json_file.close()
# =============================================================================
