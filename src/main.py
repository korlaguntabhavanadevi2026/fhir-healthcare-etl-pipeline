with open("coding_task1_output.json") as f:
    patient = json.load(f)

hl7_message = []
hl7_message.append("MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|202305011200||ADT^A01|123456|P|2.3")
hl7_message.append(f"PID|||{patient['id']}||{patient['name'][0]['family']}^{patient['name'][0]['given'][0]}||{patient.get('birthDate', '')}|{patient.get('gender', '').upper()[0]}")

with open("task_5_hl7.txt", "w") as f:
    f.write("\n".join(hl7_message))