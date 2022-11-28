from flask import Flask, jsonify, Response, request, render_template
from flask_cors import CORS
import torch
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import random
import skimage
from detecto import core

#image0 = utils.read_image('image0.jpg')
#@app.route("/")
#def index():
#    return render_template("website.html")

#def create_app():
app = Flask(__name__)
CORS(app)

matplotlib.use('agg')

labeled=['Vizsla', 'Appenzeller', 'Tibetan Mastiff']

model = core.Model.load('./model_assets/detecto_trained.pth', labeled)


@app.route("/", methods=['GET','POST'])
def predict():

    if request.method=="POST":
        print(request.form)
        print(request.files)
        #if 'file' not in request.files:
        #    return "Please try again. The Image doesn't exist"

        #image = request.files['image'].read()
        imagefile = request.files['image']
        image = skimage.io.imread(imagefile)

        predictions = model.predict(image)
        print(predictions)
        # predictions format: (labels, boxes, scores)
        labels, boxes, scores = predictions

        #Applyied thresholding
        lab=[]
        box=[]
        scor=[]
        thershold=0.6
        for i in range(len(scores)):
            if scores[i]>thershold:
                lab.append(labels[i])
                box.append(boxes[i])
                scor.append(scores[i])

        box=torch.stack(box)
        
        #fig = create_figure()
        fig,ax = plt.subplots(1)
        #Create figure original image
        ax.imshow(image)
        for i in range(len(box)):
            ax.add_patch(patches.Rectangle((box[i][0],box[i][1]),box[i][2] - box[i][0],box[i][3] - box[i][1],linewidth=1,edgecolor='r',facecolor='none'))
            ax.annotate(labels[i], xy=(box[i][0],box[i][1]), xytext=(box[i][0]+3,box[i][1]+3),color='red')
            ax.annotate(scores[i], xy=(box[i][0],box[i][1]), xytext=(box[i][0]+10,box[i][1]+20),color='red')
        
        output=io.BytesIO()
        FigureCanvas(fig).print_png(output)
        fig_output=output

        #output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image.jpg')
        # #cv2.imwrite(output_image_path, img)
        print(fig_output)
        #fig.savefig("output.png")
        #fig.show()
        output_label=lab[0]
        print(output_label)
        return render_template('website.html',output=output_label)
    else:
        output_label="No image provided"
        return render_template('website.html',output=output_label)

        #return render_template('website.html',output.getvalue(), mimetype='image/png')
        
        #if request.method == 'GET':
        #    return render_template('website.html')
        #return render_template("website.html")
        
###
#if __name__ == '__main__':
    #app.create_app()
    #app.run(host = '0.0.0.0',port=5000,debug=True, threaded=True)
#    app.run()