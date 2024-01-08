import mediapipe as mp
import cv2
import gaze


def calculate_focus_score(video_path, process_id):
    mp_face_mesh = mp.solutions.face_mesh  # initialize the face mesh model
    cap = cv2.VideoCapture(video_path)
    # cap = cv2.VideoCapture(1) 
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f'analysis/user_{process_id}_analysis.avi', fourcc, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    gaze_slopes = []

    with mp_face_mesh.FaceMesh(
            max_num_faces=1,  # number of faces to track in each frame
            refine_landmarks=True,  # includes iris landmarks in the face mesh model
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as face_mesh:
        while cap.isOpened():
            success, image = cap.read()
            if not success:  # no frame input
                break
              
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # frame to RGB for the face-mesh model
            results = face_mesh.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # frame back to BGR for OpenCV
            
            if results.multi_face_landmarks:
                slope = gaze.gaze(image, results.multi_face_landmarks[0])  # gaze estimation
                if slope:
                    gaze_slopes.append(slope)
            
            cv2.imshow('output window', image)
            # Write the frame to the video file
            out.write(image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    # Calculation
    lower_bound = 20
    upper_bound = 160
    count = sum(lower_bound <= x <= upper_bound for x in gaze_slopes)
    total_frames = len(gaze_slopes)
    return round((total_frames - count)*100/total_frames, 2)

if __name__=="__main__":
    print(calculate_focus_score('upload_data/user_7ac36cb7-806d-48e6-9842-54a7a6c13972.mp4', "234"))