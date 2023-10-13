#returns a straight IDT with a linear taper to a waveguide

import shapely as sp
import gdsfactory as gf
from gdsfactory.generic_tech import get_generic_pdk


def straight_idt(electrode_number,originx,originy,taper_length):
    
    #calculate some distances
    idt_total_width = (electrode_number*electrode_width) + ((electrode_separation*electrode_number)-electrode_separation)
    idt_separation = electrode_length + (electrode_end_margin)
    
    #this is just here for if you want to do sweeps of electrode number etc take this line out if you are planning to do sweeps
    max_idt_width = idt_total_width
    end_taper_length = taper_length
    
    
    # Create a blank component (essentially an empty GDS cell with some special features)
    c = gf.Component("Flat_IDTs")
    t = gf.Component("Text")

    
    mirror_centre = originx + pad_width + 1.5*max_idt_width + (wg_length/2) + end_taper_length
    idt_centre = originy + pad_height + pad_separation*0.5
    

    #####################################################
    #          Add Pads  + ports                        #
    #####################################################

    pad1 = c.add_polygon(
        [(originx, originx, originx+pad_width, originx+pad_width), (originy, originy+pad_height, originy+pad_height, originy)], layer=1
    )
    
    pad2 = c.add_polygon(
        [(originx, originx, originx+pad_width, originx+pad_width), (originy + pad_height + pad_separation, originy+pad_height + pad_height + pad_separation, originy+pad_height + pad_height + pad_separation, originy + pad_height + pad_separation)], layer=1
    )
    
    y_port_low_pad = originy + arm_width/2
    x_port_low_pad = originx + pad_width
    
    y_port_top_pad = originy + pad_height + pad_separation + pad_height -(arm_width/2)
    x_port_top_pad = originx + pad_width
    
    c.add_port(name = "pad_1_port",center = [x_port_low_pad,y_port_low_pad], width = arm_width, orientation = 0, layer = (1,0))
    c.add_port(name = "pad_2_port",center = [x_port_top_pad,y_port_top_pad], width = arm_width, orientation = 0, layer = (1,0))
    

    
    #####################################################
    #          add waveguide + ports                    #
    #####################################################
    
    c.add_port(name = "wg_port",center = [mirror_centre,idt_centre], width = wg_width, orientation = 180, layer = (2,0))
    waveguide = c << gf.components.rectangle(size = (wg_width,wg_length/2), layer=(2, 0))
    waveguide.connect("e2", destination = c["wg_port"])
    
    #####################################################
    #          add taper and ports                      #
    #####################################################    
    
    taper_start_x = mirror_centre-wg_length/2 - taper_length
    taper_start_y = idt_centre
    taper_end_x = mirror_centre-wg_length/2
    taper_end_y = idt_centre
    
    c.add_port(name = "taper_start", center = [taper_start_x,taper_start_y], width = idt_separation,orientation = 0, layer = (2,0))
    taper = c << gf.components.taper(length=taper_length, width1=idt_separation, width2=wg_width, layer=(2, 0))
    taper.connect("o1", destination = c["taper_start"])
    
    #####################################################
    #          add idt bus and electrodes               #
    ##################################################### 
    
    #idt bus will start with upper right point and work clockwise around polygon
    
    bus_origin_bottom = (taper_start_x, idt_centre + idt_separation/2 + arm_width) #start point for common for all bottom IDT electrodes
    bus_p2_bottom = (taper_start_x, idt_centre + idt_separation/2)
    bus_p3_bottom = (taper_start_x-idt_total_width, idt_centre + idt_separation/2)
    bus_p4_bottom =  (taper_start_x-idt_total_width, idt_centre + idt_separation/2 + arm_width)
    
    
    y_port_low_bus = idt_centre - idt_separation/2 - arm_width
    x_port_low_bus = taper_start_x - (idt_total_width/2)
          
    c.add_port(name = "lower_idt_port",center = [x_port_low_bus,y_port_low_bus], width = arm_width, orientation = 270, layer = (1,0))
    
    bus_origin_top = (taper_start_x, idt_centre - idt_separation/2)
    bus_p2_top = (taper_start_x, idt_centre - idt_separation/2 - arm_width)
    bus_p3_top = (taper_start_x-idt_total_width, idt_centre - idt_separation/2 - arm_width)
    bus_p4_top =  (taper_start_x-idt_total_width, idt_centre - idt_separation/2)
    
    y_port_top_bus = idt_centre + idt_separation/2 + arm_width
    x_port_top_bus = x_port_low_bus
    
    c.add_port(name = "upper_idt_port",center = [x_port_top_bus,y_port_top_bus], width = arm_width, orientation = 90, layer = (1,0))
        
    idt_bus_bottom = c.add_polygon([bus_origin_bottom,bus_p2_bottom,bus_p3_bottom,bus_p4_bottom],layer=(1,0))
    idt_bus_top = c.add_polygon([bus_origin_top,bus_p2_top,bus_p3_top,bus_p4_top],layer=(1,0))
    
    #### electrodes ####
    
# Loop to create the 2D array of rectangles (for electrodes)

    electrodes = []

    for i in range(electrode_number):
        # Calculate x-coordinate for the current electrode
        x1 = taper_start_x-idt_total_width +((i)*(electrode_width+electrode_separation))
        x2 = x1 + electrode_width
        y1 = idt_centre - idt_separation/2
        y2 = y1 + electrode_length
        
        # Check if the current electrode should be offset
        if i % 2 == 1:
            y1 += electrode_end_margin  # Offset for every second electrode
            y2 += electrode_end_margin
        
        electrode_i = c.add_polygon([(x1,y1),(x1,y2),(x2,y2),(x2,y1)],layer = (1,0))
        electrodes.append(electrode_i)
        
    
    #####################################################
    #          connect pad to bus                      #
    ##################################################### 
    
    #don't like the way this is done really but will do for now.
    
    route = gf.routing.get_route(c.ports["pad_1_port"],c.ports["lower_idt_port"],width = arm_width)
    c.add(route.references)
    
    route = gf.routing.get_route(c.ports["pad_2_port"],c.ports["upper_idt_port"],width = arm_width)
    c.add(route.references)
    
    #####################################################
    #         add text labels                           #
    ##################################################### 
   
    
    text = f"Elec num = {electrode_number}\nTaper l = {taper_length}\nGuide l = {wg_length}\nElec w = {electrode_width}\nElec gap = {electrode_separation}"
    
    # Create a text element
    label = c << gf.components.text(
        text=text,
        size=5,
        position=[originx - 5, originy - 5],
        justify='right',
        layer='WG'
    )
    

    
    return c



###################################
#general gds properties

originx = 0
originy = 0

###################################
#RF Probe pad dims

pad_width = 60
pad_height = 100
pad_layer = (1,0)
pad_separation = 20
#probe_separation = 
rounded_pads = True
corner_radius = 10

###################################
#IDT properties

arm_width = 15 #width of arm between pad and IDT

#note: buggy for electrode length > 110
electrode_length = 60
electrode_width = 0.25
electrode_number = 400
electrode_separation = 0.25
electrode_end_margin = 10

idt_angle = 0

###################################
#waveguide_taper_properties

wg_width = 0.350
wg_length = 10
taper_length = 100
transmission_separation = wg_length*2 + taper_length*2

################################### run

c = straight_idt(electrode_number,originx,originy,taper_length)

#show in klayout, need to install klayout live plugin

c.show()
c.write_gds("straight_idt")