from ITAP import *
import numpy as np

model_path = './ITAP press-fit v15.step'

# frequencies = [1, 10, 20, 30, 40]
# for i in range(50,901, 50):
#     frequencies.append(i)
frequencies = np.array([100, 150])
frequencies = frequencies*2*np.pi

jobs = []

# Generate model names
model_names = []
for i in range(0,len(frequencies)):
    model_name = 'Model-%d'%(i)
    model_names.append(model_name)

# Create first model
model = Model(model_names[0]) 
model.curves[0].frequency = frequencies[0]
model.new(model_path)

# Copy to subsequent models
for i in range(1,len(frequencies)):
    mdb.Model(name=model_names[i], objectToCopy=mdb.models[model_names[0]])

    mdb.models[model_names[i]].amplitudes[model.curves[0].name].setValues(
        a_0=0.0, data=((model.curves[0].a, model.curves[0].b), ), frequency=frequencies[i], start=0.0, timeSpan=STEP
    )

# Create jobs
for i in range(0,len(frequencies)):
    job_name = 'Job-' + prefix(i) + '%d_%d-Hz' %(i, frequencies[i]/(2.0*np.pi))
    Model.job(model_names[i], job_name, jobs)
