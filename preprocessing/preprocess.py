import json

def get_all_children(category,aso):
	childs = aso[category]["child_ids"]
	childs_names = []
	for child in childs:
		child_name = {}
		child_name["name"] = aso[child]["name"]
		child_name["datasets_ids"] = aso[child]["datasets_ids"]
		child_name["branch_datasets"] = aso[child]["branch_datasets"]
		if "child_ids" in aso[child]: child_name["children"] = get_all_children(child,aso)
		childs_names.append(child_name)
	if childs_names : return childs_names
		
	
def update_parent_branch_datasets(child,aso):
	parents = aso[child]["parents_ids"]
	for parent in parents:
		if aso[child]["branch_datasets"] == 1: 
			aso[parent]["branch_datasets"] = 1
		if "parents_ids" in aso[parent] : update_parent_branch_datasets(parent,aso)
	

# formating input .json to a .json format readable for this tree visualization code: https://bl.ocks.org/mbostock/4339083

# 0. read AudioSet Ontology data
with open('ontology.json') as data_file:    
	raw_aso = json.load(data_file)
with open('datasets.json') as data_file2:
	datasets = json.load(data_file2)

# 1. format data as a dictionary
## aso["/m/0dgw9r"] > {'restrictions': [u'abstract'], 'child_ids': [u'/m/09l8g', u'/m/01w250', u'/m/09hlz4', u'/m/0bpl036', u'/m/0160x5', u'/m/0k65p', u'/m/01jg02', u'/m/04xp5v', u'/t/dd00012'], 'name': u'Human sounds'}
aso = {}
for category in raw_aso:
	tmp = {}
	tmp["name"] = category["name"]	
	tmp["child_ids"] = category["child_ids"]
	tmp["parents_ids"] = []
	tmp["datasets_ids"] = []
	tmp["branch_datasets"] = 0
	for column in datasets:
		if column["parent_id"] == category["id"]:
			tmp["datasets_ids"].append(column["id"])
			tmp["name"] = tmp["name"] + "  -  [" + column["Set"] + ": " + column["Class"] + "]"
			tmp["branch_datasets"] = 1
	aso[category["id"]] = tmp

# 2. fetch higher_categories > ["/m/0dgw9r","/m/0jbk","/m/04rlf","/t/dd00098","/t/dd00041","/m/059j3w","/t/dd00123"]
for cat in aso: # find parents
	for c in aso[cat]["child_ids"]:
		aso[c]["parents_ids"].append(cat)
		update_parent_branch_datasets(c,aso)

higher_categories=[] # higher_categories are the ones without parents
for cat in aso: 
	if aso[cat]["parents_ids"] == []:
		higher_categories.append(cat)
	

# 3. format ASO properly
out_json = {}
out_json["name"] = "Ontology"
out_json["branch_datasets"] = 1
out_json["children"] = []
for category in higher_categories:
	dict_level1 = {}
	dict_level1["name"] = aso[category]["name"]
	dict_level1["datasets_ids"] = aso[category]["datasets_ids"]
	dict_level1["branch_datasets"] = aso[category]["branch_datasets"]
	dict_level1["children"] = get_all_children(category,aso)
	out_json["children"].append(dict_level1)

# 4. saving output .json
with open('./../ontology.html5.json', 'w') as f:
     json.dump(out_json, f, ensure_ascii=False)
