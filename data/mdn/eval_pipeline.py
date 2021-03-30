import json

eval_data = []
preds_data = []
total_matches = 0

eval_txt = open("data/mdn/eval.txt", "r")
for line in eval_txt:
    eval_data.append(line.lower().strip())
eval_txt.close()

preds_txt = open("data/mdn/eval-multitask-pipeline.preds", "r")
for line in preds_txt:
    preds_data.append(line.lower().strip())
preds_txt.close()

for i in range(len(eval_data)):
    eval_json = json.loads(eval_data[i])
    preds_json = json.loads(preds_data[i])
    for i in range(5):
        if eval_json["answer"][0] in preds_json[i]["span"]:
            total_matches += 1
            break
print("Total questions: {}".format(len(eval_data)))
print("Total matches: {}".format(total_matches))
print("Total % matches: {}".format((total_matches / len(eval_data)) * 100 ))