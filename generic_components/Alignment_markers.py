import shapely as sp
import gdsfactory as gf

#returns a 500um x 500um alignment marker with resist layer
#would be good to change this so that can specify sizes

  
def alignment_marker(originx, originy, minimum_width,alignment_layer,resist_layer):
    
    alignment_1 = gf.Component("alignment_1")  
    align_component = gf.Component("all alignment")
       
    corner_1 = alignment_1.add_ref(gf.components.L(width=0.5, size=[1, 1], layer=alignment_layer))
    corner_1.move(destination = (originx-335,originy-335))
    corner_2 = alignment_1.add_ref(gf.components.L(width=1, size=[3, 3], layer=alignment_layer))
    corner_2.move(destination = (originx-340,originy-340)) 
    corner_3 = alignment_1.add_ref(gf.components.L(width=2, size=[6, 6], layer=alignment_layer))
    corner_3.move(destination = (originx-348,originy-348)) 
    corner_4 = alignment_1.add_ref(gf.components.L(width=2, size=[12, 12], layer=alignment_layer))
    corner_4.move(destination = (originx-360,originy-360))  
    corner_5 = alignment_1.add_ref(gf.components.L(width=2, size=[24, 24], layer=alignment_layer))
    corner_5.move(destination = (originx-380,originy-380))  
    corner_6 = alignment_1.add_ref(gf.components.L(width=2, size=[50, 50], layer=alignment_layer))
    corner_6.move(destination = (originx-450,originy-450)) 
    corner_7 = alignment_1.add_ref(gf.components.L(width=2, size=[100, 100], layer=alignment_layer))
    corner_7.move(destination = (originx-550,originy-550))  
        
    mirror1 = alignment_1.mirror(p1 = (originx-330,originy-80), p2 = (originx-330,originy-580))
    mirror2 = mirror1.mirror(p1 = (originx-580,originy-330), p2 = (originx-80,originy-330))
    mirror3 = mirror2.mirror(p1 = (originx-330,originy-80), p2 = (originx-330,originy-580))
        
    align_bbox = alignment_1.add_polygon(points = [(originx- 80,originy-80),(originx-80,originy-580),(originx-580,originy-580),(-originx-580,originy-80)], layer = resist_layer)
    cross = alignment_1.add_ref(gf.components.align_wafer(width=0.2, spacing=1.5, cross_length=3, layer=alignment_layer, square_corner='bottom_left'))
    cross.move(destination = (originx-330,originy-330))
    #align_component << alignment_1
    align_component << alignment_1
    align_component << mirror1
    align_component << mirror2
    align_component << mirror3
    return align_component

##################################
# example variables + run        #
##################################

originx = 0
originy = 0
minimum_width = 0.2 #um
alignment_layer = (1,1000)
resist_layer = (3,1000)

align_component = alignment_marker(originx = originx, originy = originy, minimum_width = minimum_width,alignment_layer=alignment_layer,resist_layer=resist_layer)

#show in klayout, need to install klayout live plugin

align_component.show()
align_component.write_gds("Alignment markers")
