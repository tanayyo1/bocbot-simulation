import os

def box_link(name, x, y, z, l, w, h, material="Gazebo/Grey", yaw=0.0):
    return f"""
      <link name='{name}'>
        <pose>{x} {y} {z} 0 0 {yaw}</pose>
        <collision name='col'><geometry><box><size>{l} {w} {h}</size></box></geometry></collision>
        <visual name='vis'><geometry><box><size>{l} {w} {h}</size></box></geometry><material><script><name>{material}</name></script></material></visual>
      </link>"""

def cylinder_link(name, x, y, z, r, h_len, material="Gazebo/Grey", yaw=0.0):
    return f"""
      <link name='{name}'>
        <pose>{x} {y} {z} 0 0 {yaw}</pose>
        <collision name='col'><geometry><cylinder><radius>{r}</radius><length>{h_len}</length></cylinder></geometry></collision>
        <visual name='vis'><geometry><cylinder><radius>{r}</radius><length>{h_len}</length></cylinder></geometry><material><script><name>{material}</name></script></material></visual>
      </link>"""

links = []

# Floor
links.append(box_link('office_floor', 0, 0, 0.005, 30, 30, 0.01, 'Gazebo/CeilingTiled'))

# Outer Walls (White)
links.append(box_link('wall_n', 0, 15, 1.5, 30, 0.2, 3.0, 'Gazebo/White'))
links.append(box_link('wall_s', 0, -15, 1.5, 30, 0.2, 3.0, 'Gazebo/White'))
links.append(box_link('wall_e', 15, 0, 1.5, 30, 0.2, 3.0, 'Gazebo/White', yaw=1.5708))
links.append(box_link('wall_w', -15, 0, 1.5, 30, 0.2, 3.0, 'Gazebo/White', yaw=1.5708))

# Inner Main Divider Walls (Bricks)
# Horizontal Y=5
links.append(box_link('wall_h1_l', -9, 5, 1.5, 12, 0.4, 3.0, 'Gazebo/Bricks'))
links.append(box_link('wall_h1_r', 9, 5, 1.5, 12, 0.4, 3.0, 'Gazebo/Bricks'))
# Horizontal Y=-5
links.append(box_link('wall_h2_l', -9, -5, 1.5, 12, 0.4, 3.0, 'Gazebo/Bricks'))
links.append(box_link('wall_h2_r', 9, -5, 1.5, 12, 0.4, 3.0, 'Gazebo/Bricks'))

# Vertical X=-3
links.append(box_link('wall_v1_t', -3, 10, 1.5, 10, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))
links.append(box_link('wall_v1_m1', -3, 3, 1.5, 4, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))
links.append(box_link('wall_v1_m2', -3, -3, 1.5, 4, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))
links.append(box_link('wall_v1_b', -3, -10, 1.5, 10, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))

# Vertical X=3
links.append(box_link('wall_v2_t', 3, 10, 1.5, 10, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))
links.append(box_link('wall_v2_m1', 3, 3, 1.5, 4, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))
links.append(box_link('wall_v2_m2', 3, -3, 1.5, 4, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))
links.append(box_link('wall_v2_b', 3, -10, 1.5, 10, 0.4, 3.0, 'Gazebo/Bricks', yaw=1.5708))


# --- Grand Staircase (North Hallway, X=0, Y=6 to 15) ---
# 8 steps
y_start = 7.0
step_depth = 0.5
step_height = 0.12
for i in range(8):
    h = (i + 1) * step_height
    y = y_start + i * step_depth + (step_depth/2.0)
    mat = 'Gazebo/Grey' if i % 2 == 0 else 'Gazebo/DarkGrey'
    links.append(box_link(f'grand_step_{i}', 0, y, h/2.0, 5.6, step_depth, h, mat))

# Platform at the top of the stairs
plat_y_start = y_start + 8 * step_depth
plat_depth = 14.8 - plat_y_start
plat_h = 8 * step_height
links.append(box_link('grand_platform', 0, plat_y_start + plat_depth/2.0, plat_h/2.0, 5.6, plat_depth, plat_h, 'Gazebo/WoodFloor'))


# --- Left Top Room: Server Farm ---
for i in range(3):
    for j in range(4):
        x = -12 + i * 3
        y = 7 + j * 2
        links.append(box_link(f'server_{i}_{j}', x, y, 1.0, 0.8, 1.2, 2.0, 'Gazebo/Black'))


# --- Left Middle Room: Cubicles ---
# Central divider
links.append(box_link('cubicle_div_1', -9, 0, 0.6, 10, 0.2, 1.2, 'Gazebo/PaintedWall'))
# Desks
for i in [-1, 1]:
    for j in [-1, 0, 1]:
        links.append(box_link(f'desk_lm_{i}_{j}', -9 + j*3, i*2.5, 0.4, 1.6, 0.8, 0.8, 'Gazebo/Wood'))


# --- Left Bottom Room: Lounge ---
links.append(box_link('lounge_table_1', -9, -10, 0.4, 3.0, 3.0, 0.8, 'Gazebo/WoodFloor'))
# Add some cylindrical stools
for i in range(4):
    links.append(cylinder_link(f'stool_{i}', -9 + (1.5 if i%2==0 else -1.5), -10 + (1.5 if i<2 else -1.5), 0.25, 0.3, 0.5, 'Gazebo/Red'))


# --- Right Top Room: Testing Facility ---
# A ramp
# We can approximate a ramp with a few rotated boxes, but Gazebo box rotation affects collision nicely.
links.append(f"""
      <link name='test_ramp'>
        <pose>9 10 0.5 0.2 0 0</pose>
        <collision name='col'><geometry><box><size>4 6 0.2</size></box></geometry></collision>
        <visual name='vis'><geometry><box><size>4 6 0.2</size></box></geometry><material><script><name>Gazebo/Wood</name></script></material></visual>
      </link>
""")
links.append(box_link('test_platform', 9, 13.5, 0.5, 4, 2, 1.0, 'Gazebo/Wood'))

# Scattered pallets
links.append(box_link('pallet_1', 6, 6, 0.1, 1.2, 1.2, 0.2, 'Gazebo/WoodPallet'))
links.append(box_link('pallet_2', 12, 7, 0.15, 1.2, 1.2, 0.3, 'Gazebo/WoodPallet'))
links.append(box_link('pallet_3', 7, 12, 0.1, 1.2, 1.2, 0.2, 'Gazebo/WoodPallet'))


# --- Right Middle Room: Storage/Filing ---
for i in range(5):
    links.append(box_link(f'file_cab_{i}', 13, -3 + i*1.5, 1.0, 0.8, 1.0, 2.0, 'Gazebo/Grey'))
for i in range(3):
    links.append(box_link(f'storage_box_{i}', 6, -3 + i*2, 0.5, 1.5, 1.5, 1.0, 'Gazebo/WoodPallet'))


# --- Right Bottom Room: Conference Room ---
links.append(box_link('conf_table', 9, -10, 0.4, 6.0, 2.0, 0.8, 'Gazebo/Wood'))
# Screens on the wall
links.append(box_link('tv_screen_1', 14.8, -10, 1.5, 0.1, 4.0, 2.0, 'Gazebo/FlatBlack'))


sdf_content = f"""<sdf version='1.6'>
  <world name='default'>
    <!-- Lighting -->
    <light name='sun' type='directional'>
      <cast_shadows>1</cast_shadows>
      <pose>0 0 15 0 -0 0</pose>
      <diffuse>0.95 0.95 0.95 1</diffuse>
      <specular>0.3 0.3 0.3 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.3 0.3 -1.0</direction>
    </light>
    
    <model name='ground_plane'>
      <static>1</static>
      <link name='link'>
        <collision name='collision'>
          <geometry><plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
          <surface><friction><ode><mu>100</mu><mu2>50</mu2></ode></friction></surface>
        </collision>
        <visual name='visual'>
          <cast_shadows>0</cast_shadows>
          <geometry><plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri><name>Gazebo/Asphalt</name></script></material>
        </visual>
      </link>
    </model>

    <physics name='default_physics' default='0' type='ode'>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <model name='mega_office_complex'>
      <static>1</static>
      <pose>0 0 0 0 0 0</pose>
      
      {''.join(links)}
      
    </model>

    <!-- Configure the camera view to look over the entire building from the front/top -->
    <gui fullscreen='0'>
      <camera name='user_camera'>
        <pose frame=''>0.0 -22.0 25.0 0.0 0.8 1.5708</pose>
        <view_controller>orbit</view_controller>
        <projection_type>perspective</projection_type>
      </camera>
    </gui>
  </world>
</sdf>
"""

with open('/home/dipz/robot_proj/bocbot_ws/src/bocbot/worlds/boc_office.world', 'w') as f:
    f.write(sdf_content)

print("World generated successfully!")
