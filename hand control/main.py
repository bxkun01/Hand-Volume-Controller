import cv2
import mediapipe as mp
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# OpenCV video capture
cap = cv2.VideoCapture(0)

# Get the default audio device (for volume control)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, 0, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Set the initial volume to 0
volume.SetMasterVolumeLevelScalar(0.0, None)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (MediaPipe uses RGB, OpenCV uses BGR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    results = hands.process(rgb_frame)

    # Draw the hand landmarks if hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the landmarks and connections
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract coordinates for landmarks 4 (thumb tip) and 8 (index tip)
            landmarks = hand_landmarks.landmark
            h, w, _ = frame.shape

            # Get the positions of the thumb tip and index tip
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]

            # Convert coordinates to pixel values
            thumb_tip_coords = (int(thumb_tip.x * w), int(thumb_tip.y * h))
            index_tip_coords = (int(index_tip.x * w), int(index_tip.y * h))

            # Calculate the Euclidean distance between the thumb tip and index tip
            distance = math.sqrt((thumb_tip_coords[0] - index_tip_coords[0]) ** 2 +
                                 (thumb_tip_coords[1] - index_tip_coords[1]) ** 2)

            # Normalize the distance to control volume (assuming distance varies from 20 to 300 pixels)
            volume_value = min(max(distance, 20), 300)  # Clamp distance between 20 and 300 pixels
            volume_percentage = int((volume_value - 20) / (200 - 20) * 100)  # Convert to a percentage (0-100)

           
            if volume_percentage >= 100:
                volume_percentage = 100
            else:
                volume_percentage = int((volume_value - 20) / (200 - 20) * 100) 
            print(f"Volume: {volume_percentage}%")

            # Adjust the system volume based on the volume_percentage
            # Set the volume scalar (0.0 for mute, 1.0 for full volume)
            volume.SetMasterVolumeLevelScalar(volume_percentage / 100.0, None)

    # Display the frame with the hand landmarks
    cv2.imshow("Hand Landmark Detection", frame)

    # Break the loop on pressing ''
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close windows
cap.release()
cv2.destroyAllWindows()
