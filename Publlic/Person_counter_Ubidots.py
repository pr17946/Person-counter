
import cv2
import numpy as np

URL = "http://192.168.1.82"

from ubidots import ApiClient


def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Load MobileNet-SSD model which is already pre trained
prototxt = "deploy.prototxt.txt"
model = "mobilenet_iter_73000.caffemodel"
net = cv2.dnn.readNetFromCaffe(prototxt, model)

# Initialize counts
entry_count = 0
exit_count = 0

# Initialize video stream from webcam
cap = cv2.VideoCapture(URL + ":81/stream")
#cap = cv2.VideoCapture(0)

# Initialize previous people positions list and tracking dictionary
tracked_people = {}
person_id = 0
max_distance = 100
prv_entry_count = 0
prv_exit_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    (h, w) = frame.shape[:2]

    # Pre-process
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

    # Pass the blob through the network
    net.setInput(blob)
    detections = net.forward()

    # Draw the center line
    center_line_x = int(w/2)
    cv2.line(frame, (center_line_x, 0), (center_line_x, h), (0, 0, 255), 2)

    # Initialize list of people
    people_positions = []

    for i in range(detections.shape[2]):
		
        confidence = detections[0, 0, i, 2]

        #It should be greater than minimum threshold value :
        if confidence > 0.5:
            
            idx = int(detections[0, 0, i, 1])

            # Go through the loop if the detected object is person
            if idx == 15:
	
                # find x,y coordinates
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Drawing box around the object
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

                # find center point of the detected object
                person_center_x = int((startX + endX) / 2)
                person_center_y = int((startY + endY) / 2)
                person_position = (person_center_x, person_center_y)
                people_positions.append(person_position)


                # Draw the center point
                cv2.circle(frame, person_position, 5, (255, 0, 0), -1)
                
                tracked_person_id = None
                
                # Update the tracking dictionary
                min_distance = float("inf")
                for person_position in people_positions:
                    min_distance = float("inf")
                    tracked_person_id = None
                    for person_id, last_positions in tracked_people.items():
                        last_position, _ = last_positions
                        distance = euclidean_distance(person_position, last_position)
                        if distance < min_distance and distance < max_distance:
                            min_distance = distance
                            tracked_person_id = person_id
                

                if tracked_person_id is None:
                    person_id += 1
                    tracked_person_id = person_id

                tracked_people[tracked_person_id] = (person_position, tracked_people.get(tracked_person_id, (None, None))[0])
                
    # Check if people crossed the line
    for person_id, positions in tracked_people.items():
        current_position, last_position = positions
        if last_position is not None:
            if current_position[0] > center_line_x + 30 > last_position[0]:
                entry_count += 1
                tracked_people[person_id] = (current_position, None)
            elif current_position[0] < center_line_x - 30 < last_position[0]:
                exit_count += 1
                tracked_people[person_id] = (current_position, None)
            else:
                tracked_people[person_id] = (current_position, current_position)


    # Display the entry and exit count
    cv2.putText(frame, f"Entry: {entry_count}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"Exit: {exit_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    #Sending data to Ubidots cloud
    if entry_count != prv_entry_count or exit_count != prv_exit_count:
        # Initialize the Ubidots API client
        api = ApiClient(token="BBFF-GKYE5U1V2Li4i9nSOWPuqRL83bsJlA")

        # Variable id of Entry_count
        my_variable = api.get_variable('6449c29118352a000b1d9e13')

        # Name of the variable to store the data we have created in the cloud is value: "numeric" 
        new_value = my_variable.save_value({'value': entry_count})

        # Variable id of Exit_count
        my_variable = api.get_variable('6449b7a4243ec4000f86fd6f')

        # Name of the variable to store the data we have created in the cloud is value: "numeric" 
        new_value = my_variable.save_value({'value': exit_count})
        prv_entry_count = entry_count
        prv_exit_count = exit_count 
       
    
    # Showing output
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()


# In[ ]:





# In[ ]:




