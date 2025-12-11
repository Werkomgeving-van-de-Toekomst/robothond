/*
 * Jetson AGX Orin Mount voor Unitree Go2 Robot
 * 
 * Dit ontwerp is gebaseerd op:
 * - Unitree Go2 Payload specificaties: https://support.unitree.com/home/en/developer/Payload
 * - Jetson AGX Orin Developer Kit afmetingen
 * 
 * Auteur: Go2 Robot Project
 * Licentie: MIT
 * 
 * Print instellingen:
 * - Materiaal: PETG of ABS (sterker dan PLA)
 * - Layer hoogte: 0.2mm
 * - Infill: 40-50%
 * - Supports: Ja
 */

// === PARAMETERS ===

// Jetson AGX Orin afmetingen (mm)
jetson_width = 110;
jetson_depth = 110;
jetson_height = 71.65;

// Jetson mounting holes (M3, 4 hoeken)
jetson_hole_diameter = 3.2;
jetson_hole_inset = 4;  // Afstand van rand tot hole center

// Go2 payload rail afmetingen (geschat op basis van Unitree specs)
go2_rail_width = 150;       // Breedte tussen rails
go2_rail_depth = 200;       // Lengte van payload area
go2_mount_hole_diameter = 5; // M4 of M5 mounting holes
go2_mount_hole_spacing_x = 140;
go2_mount_hole_spacing_y = 180;

// Mount plaat parameters
plate_thickness = 4;
plate_width = 160;
plate_depth = 140;
plate_corner_radius = 8;

// Jetson standoff parameters
standoff_height = 15;       // Ruimte voor ventilatie
standoff_diameter = 8;
standoff_hole_diameter = 3.2;

// Ventilatie gaten
vent_hole_diameter = 10;
vent_hole_spacing = 15;

// Kabel doorvoer
cable_slot_width = 25;
cable_slot_depth = 15;

// Powerbank houder (optioneel)
include_powerbank_mount = true;
powerbank_width = 80;
powerbank_depth = 160;
powerbank_height = 30;

// Lip/rand voor extra stevigheid
lip_height = 8;
lip_thickness = 2;

// === MODULES ===

// Afgeronde rechthoek
module rounded_rect(width, depth, height, radius) {
    hull() {
        for (x = [radius, width - radius]) {
            for (y = [radius, depth - radius]) {
                translate([x, y, 0])
                    cylinder(h = height, r = radius, $fn = 32);
            }
        }
    }
}

// Ventilatie patroon
module ventilation_pattern(width, depth, hole_d, spacing) {
    cols = floor((width - hole_d) / spacing);
    rows = floor((depth - hole_d) / spacing);
    
    start_x = (width - (cols - 1) * spacing) / 2;
    start_y = (depth - (rows - 1) * spacing) / 2;
    
    for (x = [0 : cols - 1]) {
        for (y = [0 : rows - 1]) {
            translate([start_x + x * spacing, start_y + y * spacing, -1])
                cylinder(h = plate_thickness + 2, d = hole_d, $fn = 24);
        }
    }
}

// Standoff voor Jetson mounting
module standoff(height, outer_d, hole_d) {
    difference() {
        cylinder(h = height, d = outer_d, $fn = 32);
        translate([0, 0, -1])
            cylinder(h = height + 2, d = hole_d, $fn = 24);
    }
}

// Go2 mounting tab
module go2_mount_tab(hole_d) {
    tab_width = 20;
    tab_depth = 15;
    
    difference() {
        // Tab body
        hull() {
            translate([0, 0, 0])
                cylinder(h = plate_thickness, d = tab_width, $fn = 32);
            translate([0, -tab_depth/2, 0])
                cube([tab_width/2, tab_depth, plate_thickness]);
        }
        
        // Mounting hole
        translate([0, 0, -1])
            cylinder(h = plate_thickness + 2, d = hole_d, $fn = 24);
    }
}

// Kabel doorvoer slot
module cable_slot(width, depth) {
    hull() {
        translate([0, 0, -1])
            cylinder(h = plate_thickness + 2, d = depth, $fn = 24);
        translate([width - depth, 0, -1])
            cylinder(h = plate_thickness + 2, d = depth, $fn = 24);
    }
}

// Jetson retaining lip
module jetson_lip(width, depth, height, thickness) {
    // Achter lip
    translate([0, 0, plate_thickness])
        cube([width, thickness, height]);
    
    // Linker lip
    translate([0, 0, plate_thickness])
        cube([thickness, depth, height]);
    
    // Rechter lip
    translate([width - thickness, 0, plate_thickness])
        cube([thickness, depth, height]);
    
    // Voor lip (met opening voor kabels)
    translate([0, depth - thickness, plate_thickness])
        difference() {
            cube([width, thickness, height]);
            // Kabel opening
            translate([width/2 - cable_slot_width/2, -1, -1])
                cube([cable_slot_width, thickness + 2, height + 2]);
        }
}

// Powerbank houder
module powerbank_mount(width, depth, height) {
    wall = 3;
    
    translate([plate_width + 10, (plate_depth - depth) / 2, 0]) {
        difference() {
            // Outer shell
            cube([width + wall * 2, depth + wall * 2, height + plate_thickness]);
            
            // Inner cutout
            translate([wall, wall, plate_thickness])
                cube([width, depth, height + 1]);
            
            // Strap slots
            for (y = [20, depth - 10]) {
                translate([-1, wall + y, plate_thickness + height/2])
                    rotate([0, 90, 0])
                        cylinder(h = width + wall * 2 + 2, d = 5, $fn = 24);
            }
        }
    }
}

// === MAIN ASSEMBLY ===

module jetson_go2_mount() {
    difference() {
        union() {
            // Basis plaat
            rounded_rect(plate_width, plate_depth, plate_thickness, plate_corner_radius);
            
            // Jetson standoffs
            jetson_offset_x = (plate_width - jetson_width) / 2;
            jetson_offset_y = (plate_depth - jetson_depth) / 2;
            
            for (x = [jetson_hole_inset, jetson_width - jetson_hole_inset]) {
                for (y = [jetson_hole_inset, jetson_depth - jetson_hole_inset]) {
                    translate([jetson_offset_x + x, jetson_offset_y + y, plate_thickness])
                        standoff(standoff_height, standoff_diameter, standoff_hole_diameter);
                }
            }
            
            // Retaining lips
            translate([jetson_offset_x, jetson_offset_y, 0])
                jetson_lip(jetson_width, jetson_depth, lip_height, lip_thickness);
            
            // Go2 mounting tabs
            // Voorste tabs
            translate([plate_width/2 - go2_mount_hole_spacing_x/2, -10, 0])
                go2_mount_tab(go2_mount_hole_diameter);
            translate([plate_width/2 + go2_mount_hole_spacing_x/2, -10, 0])
                go2_mount_tab(go2_mount_hole_diameter);
            
            // Achterste tabs
            translate([plate_width/2 - go2_mount_hole_spacing_x/2, plate_depth + 10, 0])
                rotate([0, 0, 180])
                    go2_mount_tab(go2_mount_hole_diameter);
            translate([plate_width/2 + go2_mount_hole_spacing_x/2, plate_depth + 10, 0])
                rotate([0, 0, 180])
                    go2_mount_tab(go2_mount_hole_diameter);
            
            // Powerbank mount (optioneel)
            if (include_powerbank_mount) {
                powerbank_mount(powerbank_width, powerbank_depth, powerbank_height);
            }
        }
        
        // Ventilatie gaten in het midden
        vent_area_width = jetson_width - 30;
        vent_area_depth = jetson_depth - 30;
        
        translate([(plate_width - vent_area_width) / 2, (plate_depth - vent_area_depth) / 2, 0])
            ventilation_pattern(vent_area_width, vent_area_depth, vent_hole_diameter, vent_hole_spacing);
        
        // Kabel doorvoer slots
        // Ethernet kabel slot (achter)
        translate([plate_width/2, plate_depth - 20, 0])
            cable_slot(cable_slot_width, cable_slot_depth);
        
        // Power kabel slot (zijkant)
        translate([plate_width - 20, plate_depth/2, 0])
            rotate([0, 0, 90])
                cable_slot(cable_slot_width, cable_slot_depth);
    }
}

// === RENDER ===

// Render de mount
jetson_go2_mount();

// Preview text (alleen zichtbaar in OpenSCAD)
// translate([plate_width/2, -25, 0])
//     linear_extrude(1)
//         text("Jetson AGX Orin Mount", size=8, halign="center");

