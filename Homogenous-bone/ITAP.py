# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

# Python-specific packages
import math
# import numpy as np
def prefix(i):
    return "0" if i < 10 else ""

class Curve:
    def __init__(self, a, b, name, frequency):
        self.a = a
        self.b = b
        self.name = name
        self.frequency = frequency
class Force:
    def __init__(self, curve_name, offset, direction):
        self.curve_name = curve_name
        self.offset_from_spigot = offset
        self.direction = direction

class Model:
    def __init__(self, model_name):
        self.curves = [
            Curve(200e-6, 0, "Cos", 2*math.pi*100)
        ]
        self.forces = [
            Force(self.curves[0].name, 0.001, (0.0, 0.0, -1.0))
        ]
        self.model_name = model_name
        self.mesh_size = 3e-3
        self.stem_height = 0.12
        self.stem_radius_proximal = 0.006
        self.stem_radius_distal = 0.0035
        self.collar_radius = 0.014
        self.collar_height = 0.006
        self.spigot_height = 0.045
        self.spigot_radius = 0.009
        self.stem_fillet = 0.0045
        self.cement_thickness = 0.001
        self.bone_height = 0.18
        self.bone_thickness = 0.002
        self.sensors = ['sensor_stem', 'sensor_collar', 'sensor_spigot', "sensor_flange"]
        self.period = 2*math.pi*6.0/(self.curves[0].frequency)
        self.increment = 2*math.pi*1/(self.curves[0].frequency*30.0)
        mdb.Model(modelType=STANDARD_EXPLICIT, name=model_name)
    def __set_force_offset__(self, force_offset, part):
        mdb.models[self.model_name].parts[part].DatumPlaneByPrincipalPlane(
        offset=force_offset, principalPlane=XZPLANE
        )
        mdb.models[self.model_name].parts[part].PartitionCellByDatumPlane(
            cells= mdb.models[self.model_name].parts[part].cells.getSequenceFromMask(('[#f ]', ), ),
            datumPlane=mdb.models[self.model_name].parts[part].datums[6]
        )
    def __horizontal_partition__(self, name):
        mdb.models[self.model_name].parts[name].DatumPlaneByPrincipalPlane(offset=0.02, principalPlane=XZPLANE)
        mdb.models[self.model_name].parts[name].PartitionCellByDatumPlane(
            cells=mdb.models[self.model_name].parts[name].cells.getSequenceFromMask(('[#f ]', ), ),
            datumPlane=mdb.models[self.model_name].parts[name].datums[6]
        )
    def __assign_material__(self, name, range):
        mdb.models[self.model_name].parts[name].SectionAssignment(
            offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
            region=Region(cells=mdb.models[self.model_name].parts[name].cells.getSequenceFromMask(mask=(range, ), )),
            sectionName='Section-1', thicknessAssignment=FROM_SECTION
        )
    def __mesh_part__(self, name, size, region):
        mdb.models[self.model_name].parts[name].setMeshControls(
            elemShape=TET, regions=mdb.models[self.model_name].parts[name].cells.getSequenceFromMask((region, ), ), technique=FREE
        )
        mdb.models[self.model_name].parts[name].setElementType(
            elemTypes=(
                ElemType( elemCode=C3D20R, elemLibrary=STANDARD),
                ElemType(elemCode=C3D15, elemLibrary=STANDARD),
                ElemType(elemCode=C3D10, elemLibrary=STANDARD)
            ), 
            regions=(mdb.models[self.model_name].parts[name].cells.getSequenceFromMask((region, ), ), )
        )
        mdb.models[self.model_name].parts[name].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=size)
        mdb.models[self.model_name].parts[name].generateMesh()
    def __output_requests__(self, sensors):
        for sensor in sensors:
            mdb.models[self.model_name].FieldOutputRequest(
                createStepName='Step-1', frequency=1, 
                name=sensor, rebar=EXCLUDE, region=mdb.models[self.model_name].rootAssembly.sets[sensor],
                sectionPoints=DEFAULT, variables=('U', )
            )
            mdb.models[self.model_name].HistoryOutputRequest(
                createStepName="Step-1", frequency = 1, name=sensor, rebar=EXCLUDE,
                region= mdb.models[self.model_name].rootAssembly.sets[sensor],
                sectionPoints=DEFAULT, variables=('U1', 'U2', 'U3'),
            )
        del mdb.models[self.model_name].historyOutputRequests['H-Output-1']
        mdb.models[self.model_name].fieldOutputRequests['F-Output-1'].setValues(
            frequency=1, 
            variables=('U', )
        )
    def __create_materials__(self):
        mdb.models[self.model_name].Material(name="Titanium")
        mdb.models[self.model_name].materials["Titanium"].Density(table=((4430, ), ))
        mdb.models[self.model_name].materials["Titanium"].Elastic(table=((114e9, 0.33), ))
        mdb.models[self.model_name].HomogeneousSolidSection(material="Titanium", name='Section-1', thickness=None)
        
        mdb.models[self.model_name].Material(name='bone')
        mdb.models[self.model_name].materials['bone'].setValues(materialIdentifier='')
        mdb.models[self.model_name].materials['bone'].setValues(description='')
        mdb.models[self.model_name].materials['bone'].Elastic(
            dependencies=0, moduli= LONG_TERM, noCompression=OFF, noTension=OFF,
            table=((12000000000.0, 20000000000.0, 13400000000.0, 0.22, 0.38, 0.35, 5610000000.0, 4530000000.0, 6230000000.0), ),
            temperatureDependency=OFF, type=ENGINEERING_CONSTANTS
        )
        mdb.models[self.model_name].materials['bone'].Density(table=((2000.0, ), ))

        mdb.models[self.model_name].Material(name='PMMA')
        mdb.models[self.model_name].materials['PMMA'].setValues(materialIdentifier='')
        mdb.models[self.model_name].materials['PMMA'].setValues(description='')
        mdb.models[self.model_name].materials['PMMA'].Elastic(
            dependencies=0, moduli=LONG_TERM, noCompression=OFF, noTension=OFF, table=((2000000000.0, 0.4), ), 
        temperatureDependency=OFF, type=ISOTROPIC
            )
        mdb.models[self.model_name].materials['PMMA'].Density(table=((1180.0, ), ))
    def __assemble__(self):
        mdb.models[self.model_name].rootAssembly.DatumCsysByDefault(CARTESIAN)
        mdb.models[self.model_name].rootAssembly.Instance(dependent=ON, name='spigot-1', part=mdb.models[self.model_name].parts["spigot"])
        mdb.models[self.model_name].rootAssembly.Instance(dependent=ON, name='collar-1', part=mdb.models[self.model_name].parts["collar"])
        mdb.models[self.model_name].rootAssembly.Instance(dependent=ON, name='flange-1', part=mdb.models[self.model_name].parts["flange"])
        mdb.models[self.model_name].rootAssembly.Instance(dependent=ON, name='stem-1', part=mdb.models[self.model_name].parts["stem"])
        mdb.models[self.model_name].rootAssembly.Instance(dependent=ON, name='bone-1', part= mdb.models[self.model_name].parts['bone'])
        mdb.models[self.model_name].rootAssembly.Instance(dependent=ON, name='cement-1', part=mdb.models[self.model_name].parts['cement'])
        ############################### Give names ###############################
        mdb.models[self.model_name].rootAssembly.Surface(name='spigot-top', side1Faces= mdb.models[self.model_name].rootAssembly.instances['spigot-1'].faces.getSequenceFromMask(('[#4000 ]', ), ))
        mdb.models[self.model_name].rootAssembly.Surface(name='flange-inner', side1Faces=mdb.models[self.model_name].rootAssembly.instances['flange-1'].faces.getSequenceFromMask(('[#400000 ]', ), ))

        mdb.models[self.model_name].rootAssembly.Surface(name='collar-top', side1Faces=mdb.models[self.model_name].rootAssembly.instances['collar-1'].faces.getSequenceFromMask(('[#44 ]', ), ))
        mdb.models[self.model_name].rootAssembly.Surface(name='collar-bottom', side1Faces=mdb.models[self.model_name].rootAssembly.instances['collar-1'].faces.getSequenceFromMask(('[#82 ]', ), ))
        mdb.models[self.model_name].rootAssembly.Surface(name='stem-bottom', side1Faces=mdb.models[self.model_name].rootAssembly.instances['stem-1'].faces.getSequenceFromMask(('[#10004 ]', ), ))
        mdb.models[self.model_name].rootAssembly.Surface(
            name='stem',
            side1Faces=mdb.models[self.model_name].rootAssembly.instances['stem-1'].faces.getSequenceFromMask(('[#7b60 ]', ), )
        )
        mdb.models[self.model_name].rootAssembly.Surface(
            name='cement-inner',
            side1Faces=mdb.models[self.model_name].rootAssembly.instances['cement-1'].faces.getSequenceFromMask(('[#8 ]', ), )
        )
        mdb.models[self.model_name].rootAssembly.Surface(
            name='bone-inner', 
            side1Faces=mdb.models[self.model_name].rootAssembly.instances['bone-1'].faces.getSequenceFromMask(('[#8 ]', ), )
        )
        mdb.models[self.model_name].rootAssembly.Surface(
            name='cement-outer',
            side1Faces=mdb.models[self.model_name].rootAssembly.instances['cement-1'].faces.getSequenceFromMask(('[#2 ]', ), )
        )

    def __tie__(self):
        mdb.models[self.model_name].Tie(
            adjust=ON, main= mdb.models[self.model_name].rootAssembly.surfaces['collar-top'],
            name= 'Constraint-1', positionToleranceMethod=COMPUTED, secondary= mdb.models[self.model_name].rootAssembly.surfaces['stem-bottom'],
            thickness=ON, tieRotations=ON
        )
        mdb.models[self.model_name].Tie(
            adjust=ON, main=mdb.models[self.model_name].rootAssembly.surfaces['collar-bottom'],
            name= 'Constraint-2', positionToleranceMethod=COMPUTED, secondary=mdb.models[self.model_name].rootAssembly.surfaces['spigot-top'],
            thickness=ON, tieRotations=ON
        )
        mdb.models[self.model_name].Tie(
            adjust=ON, main= mdb.models[self.model_name].rootAssembly.surfaces['flange-inner'],
            name= 'Constraint-3', positionToleranceMethod=COMPUTED, secondary=Region( faces=mdb.models[self.model_name].rootAssembly.instances['spigot-1'].faces.getSequenceFromMask(mask=('[#2000 ]', ), )),
            thickness=ON, tieRotations=ON
        )
        mdb.models[self.model_name].ContactProperty('rough-hard_contact')
        mdb.models[self.model_name].interactionProperties['rough-hard_contact'].TangentialBehavior( formulation=ROUGH)
        mdb.models[self.model_name].interactionProperties['rough-hard_contact'].NormalBehavior( allowSeparation=ON, constraintEnforcementMethod=DEFAULT,  pressureOverclosure=HARD)
        mdb.models[self.model_name].ContactStd(createStepName='Initial', name='Int-1')
        mdb.models[self.model_name].interactions['Int-1'].includedPairs.setValuesInStep(stepName='Initial', useAllstar=ON)
        mdb.models[self.model_name].interactions['Int-1'].contactPropertyAssignments.appendInStep(
            assignments=((GLOBAL, SELF, 'rough-hard_contact'), ), stepName='Initial'
        )
        mdb.models[self.model_name].SurfaceToSurfaceContactStd(
            adjustMethod=NONE, clearanceRegion=None, createStepName='Initial', datumAxis=None, initialClearance=OMIT, interactionProperty='rough-hard_contact', main=mdb.models[self.model_name].rootAssembly.surfaces['stem'], name='Int-2', secondary=mdb.models[self.model_name].rootAssembly.surfaces['cement-inner'], sliding=FINITE, thickness=ON
        )
        mdb.models[self.model_name].SurfaceToSurfaceContactStd(
            adjustMethod=NONE, clearanceRegion=None, createStepName='Initial', datumAxis=None, initialClearance=OMIT, interactionProperty='rough-hard_contact', main=mdb.models[self.model_name].rootAssembly.surfaces['cement-outer'], name='Int-3', secondary=mdb.models[self.model_name].rootAssembly.surfaces['bone-inner'], sliding=FINITE, thickness=ON
        )
    def __points_of_interest__(self):
        mdb.models[self.model_name].rootAssembly.Set(
            name='force_point', vertices=mdb.models[self.model_name].rootAssembly.instances['spigot-1'].vertices.getSequenceFromMask(('[#1 ]', ), )
        )
        mdb.models[self.model_name].rootAssembly.ReferencePoint(point=mdb.models[self.model_name].rootAssembly.instances['spigot-1'].vertices[0])

        mdb.models[self.model_name].rootAssembly.Set(
            name='sensor_stem', vertices=mdb.models[self.model_name].rootAssembly.instances['stem-1'].vertices.findAt(((0.0, 166.556246e-3, 4.555547e-3), ))
        )
        mdb.models[self.model_name].rootAssembly.Set(
            name='sensor_spigot', vertices=mdb.models[self.model_name].rootAssembly.instances['spigot-1'].vertices.findAt(((0.0, 1.0e-3, 7.0e-3), ))
        )
        mdb.models[self.model_name].rootAssembly.Set(
            name='sensor_flange', vertices=mdb.models[self.model_name].rootAssembly.instances['flange-1'].vertices.findAt(((0.0, 50.973324e-3, 21.07129e-3), ))
        )
        mdb.models[self.model_name].rootAssembly.Set(
            name='sensor_collar', vertices=mdb.models[self.model_name].rootAssembly.instances['collar-1'].vertices.getSequenceFromMask(('[#1 ]', ), )
    )
    def __boundaries__(self):
    #     mdb.models[self.model_name].rootAssembly.Set(
    #         name='vise_points', vertices= mdb.models[self.model_name].rootAssembly.instances['stem-1'].vertices.getSequenceFromMask(('[#3 ]', ), )
    # )
    #     mdb.models[self.model_name].EncastreBC(
    #         createStepName='Initial', localCsys=None, name='BC-1', region=mdb.models[self.model_name].rootAssembly.sets['vise_points']
    #     )
        mdb.models[self.model_name].PinnedBC(
            createStepName='Initial', localCsys=None, name='BC-1',
            region=Region(faces=mdb.models[self.model_name].rootAssembly.instances['bone-1'].faces.getSequenceFromMask(mask=('[#1 ]', ), ))
        )
    def __step__(self):
        # period = 0.6 if 40.0/self.curves[0].frequency < 0.6 else 40.0/self.curves[0].frequency
        mdb.models[self.model_name].ImplicitDynamicsStep(
            initialInc=self.increment,  maxNumInc= int(1e7),
            name='Step-1', noStop=OFF, nohaf=OFF, previous='Initial', timeIncrementationMethod=FIXED, 
            timePeriod=self.period
        )
    def __apply_force__(self, force, i):
        # mdb.models[self.model_name].ConcentratedForce(
        #     amplitude=force.curve_name,
        #     cf1=force.direction[0], cf2=force.direction[1], cf3=force.direction[2],
        #     createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-'+str(i),
        #     region= mdb.models[self.model_name].rootAssembly.sets['force_point']
        # )
        mdb.models[self.model_name].DisplacementBC(
            amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-2', region=mdb.models[self.model_name].rootAssembly.sets['force_point'], u1=UNSET, u2=UNSET, u3=1.0, ur1=UNSET, ur2=UNSET, ur3=UNSET
        )
        mdb.models[self.model_name].boundaryConditions['BC-2'].setValues(amplitude=force.curve_name, u3=-1.0)
    def __create_curve__(self, amp_a, amp_b, name, freq):
        # def HanningWind(freq, t_final, delta_t , amp):
        #     t = np.arange(0, (t_final+delta_t), delta_t)
        #     cosi = amp * np.cos(2 * np.pi * freq * t)
        #     HannWind = np.hanning(len(t))
        #     y = cosi * HannWind
        #     ListOfTuples = []
        #     for i in range(len(y)):
        #         timestamp = [t[i], y[i]]
        #         ListOfTuples.append(tuple(timestamp))
        #     # ListOfTuples[-1][1]=0.0
        #     return tuple(ListOfTuples)
        # mdb.models[self.model_name].TabularAmplitude(
        #     data=HanningWind(self.frequency,(3.0/self.frequency), 1e-4,self.amplitude),
        #     name=self.curve_name, smooth=SOLVER_DEFAULT, timeSpan=STEP
        # )
        mdb.models[self.model_name].PeriodicAmplitude(
            a_0=0.0, data=((amp_a, amp_b), ), frequency=freq, name=name, start=0.0, timeSpan=STEP
        )
    def __import_model__(self, model_path):
        ########### Import
        mdb.openStep(model_path, scaleFromFile=OFF)
        mdb.models[self.model_name].PartFromGeometryFile(
            combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='spigot', scale=0.001, type=DEFORMABLE_BODY
        )
        mdb.models[self.model_name].PartFromGeometryFile(
            bodyNum=2, combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='collar', scale=0.001, type=DEFORMABLE_BODY
        )
        mdb.models[self.model_name].PartFromGeometryFile(
            bodyNum=3, combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='stem', scale=0.001, type=DEFORMABLE_BODY
        )
        mdb.models[self.model_name].PartFromGeometryFile(
            bodyNum=4, combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='rotation-teeth', scale=0.001, type=DEFORMABLE_BODY
        )
        mdb.models[self.model_name].PartFromGeometryFile(
            bodyNum=5, combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='flange', scale=0.001, type=DEFORMABLE_BODY
        )
        ##################### Spigot partitioning
        mdb.models[self.model_name].ConstrainedSketch(gridSpacing=0.001, name='__profile__', 
            sheetSize=0.057, transform=
            mdb.models[self.model_name].parts['spigot'].MakeSketchTransform(
            sketchPlane=mdb.models[self.model_name].parts['spigot'].faces[6], 
            sketchPlaneSide=SIDE1, 
            sketchUpEdge=mdb.models[self.model_name].parts['spigot'].edges[5], 
            sketchOrientation=RIGHT, origin=(0.0, 0.01425, 0.007))
        )
        mdb.models[self.model_name].sketches['__profile__'].sketchOptions.setValues(decimalPlaces=3)
        mdb.models[self.model_name].parts['spigot'].projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=mdb.models[self.model_name].sketches['__profile__'])
        mdb.models[self.model_name].sketches['__profile__'].Line(point1=(-0.00529150250385489, -0.007), point2=(0.00529150248048348, -0.007))
        mdb.models[self.model_name].sketches['__profile__'].Line(point1=(0.0, 0.0132500004470348), point2=(0.0, -0.0132500000381842))

        mdb.models[self.model_name].parts['spigot'].PartitionFaceBySketch(faces=mdb.models[self.model_name].parts['spigot'].faces.getSequenceFromMask(('[#40 ]', ), ), sketch=mdb.models[self.model_name].sketches['__profile__'], sketchUpEdge=mdb.models[self.model_name].parts['spigot'].edges[5])
        del mdb.models[self.model_name].sketches['__profile__']

        ########################## Collar
        mdb.models[self.model_name].parts['collar'].DatumPlaneByPrincipalPlane(offset=0.0, principalPlane=YZPLANE)
        mdb.models[self.model_name].parts['collar'].PartitionCellByDatumPlane(
            cells=mdb.models[self.model_name].parts['collar'].cells.getSequenceFromMask(('[#1 ]', ), ),
            datumPlane=mdb.models[self.model_name].parts['collar'].datums[2]
        )

        ########################## Stem

        mdb.models[self.model_name].parts['stem'].DatumPlaneByPrincipalPlane(offset=0.08, principalPlane=XZPLANE)
        mdb.models[self.model_name].parts['stem'].PartitionCellByDatumPlane(
            cells= mdb.models[self.model_name].parts['stem'].cells.getSequenceFromMask(('[#1 ]', ), ), datumPlane=mdb.models[self.model_name].parts['stem'].datums[2]
        )
        mdb.models[self.model_name].parts['stem'].PartitionCellByPlaneThreePoints(
            cells=mdb.models[self.model_name].parts['stem'].cells.getSequenceFromMask(('[#3 ]', ), ),
            point1=mdb.models[self.model_name].parts['stem'].vertices[1],
            point2= mdb.models[self.model_name].parts['stem'].vertices[0],
            point3= mdb.models[self.model_name].parts['stem'].vertices[3]
        )
    def __create_cement__(self):
        mdb.models[self.model_name].ConstrainedSketch(name='__profile__', sheetSize=0.342)
        mdb.models[self.model_name].sketches['__profile__'].sketchOptions.setValues(sheetSize=0.342)
        mdb.models[self.model_name].sketches['__profile__'].sketchOptions.setValues(gridOrigin=(0.0, self.spigot_height + self.collar_height))
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal,                         self.spigot_height + self.collar_height),
            point2=(self.stem_radius_proximal + self.cement_thickness, self.spigot_height + self.collar_height)
        )
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal + self.cement_thickness, self.spigot_height + self.collar_height                   ),
            point2=(self.stem_radius_proximal + self.cement_thickness, self.spigot_height + self.collar_height + self.stem_height)
        )
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal + self.cement_thickness, self.spigot_height + self.collar_height + self.stem_height), 
            point2=(self.stem_radius_distal   + self.cement_thickness, self.spigot_height + self.collar_height + self.stem_height)
        )
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_distal + self.cement_thickness, self.spigot_height + self.collar_height + self.stem_height),
            point2=(self.stem_radius_proximal                      , self.spigot_height + self.collar_height                   )
        )
        mdb.models[self.model_name].sketches['__profile__'].ConstructionLine(point1=(0.0, 0.1675), point2=(0.0, 0.15250000004191))
        mdb.models[self.model_name].Part(dimensionality=THREE_D, name='cement', type=DEFORMABLE_BODY)
        mdb.models[self.model_name].parts['cement'].BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF, sketch=mdb.models[self.model_name].sketches['__profile__'])
        del mdb.models[self.model_name].sketches['__profile__']

        ###################### Assign material
        mdb.models[self.model_name].parts['cement'].SectionAssignment(offset=0.0, 
            offsetField='', offsetType=MIDDLE_SURFACE,
            region=Region(cells=mdb.models[self.model_name].parts['cement'].cells.getSequenceFromMask(mask=('[#1 ]', ), )),
            sectionName='Section-1', thicknessAssignment= FROM_SECTION
        )
        mdb.models[self.model_name].HomogeneousSolidSection(material='PMMA', name='PMMA', thickness=None)
        mdb.models[self.model_name].parts['cement'].sectionAssignments[0].setValues( sectionName='PMMA')
    def __create_bone__(self):
        mdb.models[self.model_name].ConstrainedSketch(name='__profile__', sheetSize=0.48)
        mdb.models[self.model_name].sketches['__profile__'].ConstructionLine(point1=(0.0, -0.24), point2=(0.0, 0.24))
        mdb.models[self.model_name].sketches['__profile__'].sketchOptions.setValues(gridOrigin=(0.0, self.spigot_height + self.collar_height))
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal + self.cement_thickness, self.spigot_height + self.collar_height),       
            point2=(self.stem_radius_proximal + self.cement_thickness + self.bone_thickness, self.spigot_height + self.collar_height),  
        )
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal + self.cement_thickness + self.bone_thickness, self.spigot_height + self.collar_height),
            point2=(self.stem_radius_proximal + self.cement_thickness + self.bone_thickness, self.bone_height + self.spigot_height + self.collar_height )
        )
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal + self.cement_thickness + self.bone_thickness, self.bone_height + self.spigot_height + self.collar_height),
            point2=(self.stem_radius_proximal + self.cement_thickness, self.bone_height + self.spigot_height + self.collar_height)
        )
        mdb.models[self.model_name].sketches['__profile__'].Line(
            point1=(self.stem_radius_proximal + self.cement_thickness, self.bone_height + self.spigot_height + self.collar_height),
            point2=(self.stem_radius_proximal + self.cement_thickness, self.spigot_height + self.collar_height)
        )
        mdb.models[self.model_name].Part(dimensionality=THREE_D, name='bone', type=
            DEFORMABLE_BODY)
        mdb.models[self.model_name].parts['bone'].BaseSolidRevolve(angle=360.0, 
            flipRevolveDirection=OFF, sketch=
            mdb.models[self.model_name].sketches['__profile__'])
        del mdb.models[self.model_name].sketches['__profile__']
        mdb.models[self.model_name].HomogeneousSolidSection(material='bone', name='bone', 
            thickness=None)
        mdb.models[self.model_name].parts['bone'].SectionAssignment(offset=0.0, offsetField=
            '', offsetType=MIDDLE_SURFACE, region=Region(
            cells=mdb.models[self.model_name].parts['bone'].cells.getSequenceFromMask(mask=(
            '[#1 ]', ), )), sectionName='bone', thicknessAssignment=FROM_SECTION)

        mdb.models[self.model_name].parts['bone'].DatumCsysByThreePoints(
            coordSysType= CYLINDRICAL, line1=(1.0, 0.0, 0.0), line2=(0.0, 0.0, -1.0),
            name= 'Datum csys-1', origin=(0.0, 0.0, 0.0)
            )
        mdb.models[self.model_name].parts['bone'].MaterialOrientation(
            additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0 , axis=AXIS_3,
            fieldName='', localCsys= mdb.models[self.model_name].parts['bone'].datums[3], orientationType=SYSTEM,
            region=Region( cells=mdb.models[self.model_name].parts['bone'].cells.getSequenceFromMask(mask=( '[#1 ]', ), )), stackDirection=STACK_3
        )
    @property
    def frequency(self):
        return self.curves[0].frequency
    @frequency.setter
    def frequency(self, freq):
        self.curves[0].frequency = 2*math.pi*freq
    @staticmethod
    def job(model_name, job_name, job_list):
        mdb.Job(
            atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE,
            model=model_name,
            name=job_name, 
            nodalOutputPrecision=SINGLE, numCpus=6, numDomains=6, numGPUs=0, 
            numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='',
            type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0, modelPrint=OFF, multiprocessingMode=DEFAULT,
        )
        job_list.append(job_name)
    def new(self, model_path):
        self.__import_model__(model_path)
        ############################### Materials ###############################
        self.__create_materials__()

        ############################### Assign material ###############################
        self.__assign_material__("collar", '[#f ]')
        self.__assign_material__("spigot",'[#1 ]')
        self.__assign_material__("stem", "[#ff ]")
        self.__assign_material__("flange", "[#1 ]")
        self.__create_cement__()
        self.__create_bone__()

        ############################### Assemble ###############################
        self.__assemble__()
        self.__tie__()

        ############################### _mesh ###############################
        self.__mesh_part__("stem", self.mesh_size,"[#f ]")
        self.__mesh_part__("collar", self.mesh_size,"[#f ]")
        self.__mesh_part__("spigot", self.mesh_size,"[#f ]")
        self.__mesh_part__("flange", self.mesh_size,"[#f ]")
        self.__mesh_part__("bone", self.mesh_size,"[#f ]")
        self.__mesh_part__("cement", self.mesh_size,"[#f ]")

        ############################## Create points of interest ###############################
        self.__points_of_interest__()
        self.__boundaries__()
        self.__step__()

        ############################### Request outputs ###############################

        self.__output_requests__(self.sensors)
        ############################### Apply periodic force ###############################
        
        for curve in self.curves:
            self.__create_curve__(curve.a, curve.b, curve.name, curve.frequency)
        for i, force in enumerate(self.forces):
            self.__apply_force__(force, i)
        mdb.models[self.model_name].rootAssembly.regenerate()

jobs = []
models = []




