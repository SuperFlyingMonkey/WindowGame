import tkinter as tk
import math

class Game:
    def __init__(self, master, map_data):
        self.master = master
        
        self.master.title("Game")
        
        # Get initial window size
        self.height = master.winfo_screenheight()
        self.width = master.winfo_screenwidth()
        
        # Set initial window geometry and background color
        self.master.attributes('-fullscreen',True)
        self.master.config(cursor="none")
        self.player_x = 80
        self.player_y = 80
        self.movment_speed = 2
        self.count = 0
        self.tile_size =16
        self.start_check = False
        self.map = map_data
        self.player_angle = 20
        self.prev_player_angle = 0
        # Create the canvas
        self.canvas = tk.Canvas(master, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.wall_color = (105,105,105)
        self.create_background()
        self.render_map()

        # Bind the window resize event
        self.master.bind("<Configure>", self.on_resize)

        # Set frame rate and keypress handling
        self.frame_rate = 60
        self.angle = 0
        self.pressed_keys = set()
        self.master.bind_all("<KeyPress>", self.key_pressed)
        self.master.bind_all("<KeyRelease>", self.key_released)
        self.master.bind("<Escape>", self.close_game)
        self.ignore_event = False
        
        # Start the game loop 

        
        self.update_game()



        
    def key_pressed(self, event): 
        """Handles key press events."""
        self.pressed_keys.add(event.keysym)

    def key_released(self, event):
        """Handles key release events."""
        if event.keysym in self.pressed_keys:
            self.pressed_keys.remove(event.keysym)

    def close_game(self, event):
        print("Game Closed")
        root.destroy()

    def update_game(self):
        """Updates the game state and redraws everything."""

        self.move_delta = self.player_x + self.player_y
        self.master.bind("<Motion>", self.mouse_movment)
        self.movement()
        self.centre_mouse()
        
        # Ensure player_angle wraps around properly
        self.player_angle %= 2 * math.pi
        self.fov = 80 
        self.num_rays =  max(60, self.width//5)  # Number of rays to cast
        
        #clear canvas only when player move or rotates
        if self.move_delta != self.player_x+self.player_y or self.prev_player_angle != self.player_angle:
            self.canvas.delete("wall")
            for i in range(self.num_rays):
                ray_angle = (self.player_angle) + (self.fov / self.num_rays) * (i - self.num_rays /2) * (math.pi / 180)  # Convert degrees to radians
                self.cast_ray(self.player_x, self.player_y, ray_angle)
        self.prev_player_angle = self.player_angle 

        # Schedule the next frame 
        self.master.after(self.frame_rate, self.update_game)

    def collision_check(self,next_x,next_y):
        self.player_tile_x = int(next_x//self.tile_size)
        self.player_tile_y = int(next_y//self.tile_size)

        if self.map[self.player_tile_y][self.player_tile_x]==1:
            return True
        else:
            return False
        
    def centre_mouse(self):
        self.ignore_event = True
        self.master.event_generate('<Motion>', warp=True, x=self.width // 2, y=self.height // 2)
    def mouse_movment(self, event):
        if self.ignore_event:
            self.ignore_event = False
            return
        centre_x = self.master.winfo_width()//2
        mouse_x = event.x
            
        delta_x = mouse_x-centre_x

        #self.canvas.delete("all")
        sensitivity = 0.0003
        self.player_angle += delta_x*sensitivity

        self.player_angle %= 2 * math.pi
        self.centre_mouse()        

    def movement(self):
        forward_x = self.movment_speed * math.cos(self.player_angle)
        forward_y = self.movment_speed * math.sin(self.player_angle)
        strafe_angle = self.player_angle + (math.pi/2)
        strafe_x = self.movment_speed * math.cos(strafe_angle)
        strafe_y = self.movment_speed * math.sin(strafe_angle)

        move_x,move_y = 0,0
        

        if "w" in self.pressed_keys:
            move_x += forward_x
            move_y += forward_y
            
        if "s" in self.pressed_keys:
            move_x -= forward_x
            move_y -= forward_y
            
        if "a" in self.pressed_keys:
            move_x -= strafe_x
            move_y -= strafe_y
            
        if "d" in self.pressed_keys:
            move_x += strafe_x
            move_y += strafe_y
            
        next_x = self.player_x + move_x
        next_y = self.player_y + move_y
        if not self.collision_check(next_x, next_y):
            self.player_x = next_x
            self.player_y = next_y

            




    def create_background(self):
        """Creates and redraws the background."""
        self.canvas.create_rectangle(0, 0, self.width, self.height // 2, fill="#696969")  # Sky
        self.canvas.create_rectangle(0, self.height // 2, self.width, self.height, fill="#696969")  # Ground

    def on_resize(self, event):
        """Handles window resize events."""
        self.width = event.width
        self.height = event.height

        # Update the canvas dimensions and redraw the background and map
        self.canvas.config(width=self.width, height=self.height)
        self.create_background()
        #self.render_map()
    

    def render_map(self):
        """Renders the map grid."""
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                x1 = x * self.tile_size
                y1 = y * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size

                #Draw tile on map colour them based on type of tile and implement characteristics of said tile (0= empty space 1= wall 2= player spawn)
                #if tile == 1:
                    #self.canvas.create_rectangle(x1, y1, x2, y2, fill="grey")
                    
                if tile == 2 and self.start_check == False:  
                    self.player_x = x2-8
                    self.player_y = y2-8
                    self.start_check = True
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="green")

                #elif tile == 0:
                    #self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")

    def apply_ambient_light(self, distance):
    # Add the ambient color to the wall color, ensuring values stay within range
        
        max_brightness = 60
        min_brightness = 5



        ambient_color = max(min_brightness,max_brightness -distance)
        
        final_color = (
        min(self.wall_color[0] + int(ambient_color), 255),
        min(self.wall_color[1] + int(ambient_color), 255),
        min(self.wall_color[2] + int(ambient_color), 255)
    )
        return self.rgb_to_hex(final_color)
    
    def rgb_to_hex(self,rgb):
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def draw_2D_World(self, ray_x, ray_y, ray_angle):
        # Calculate the distance from the player to the wall
        ray_length = math.sqrt((ray_x - self.player_x)**2 + (ray_y - self.player_y)**2)
        #ray_length = ray_length * math.cos(self.player_angle-ray_angle)
    
        
    
        # Calculate the height of the line based on distance (inverse relation)
        HEIGHT_CONSTANT = self.height * 10  
        if ray_length > 0:
            line_height = HEIGHT_CONSTANT / ray_length
        else:
            line_height = self.height  # Full height if ray_length is zero (very close)

        # Set a fixed width for each ray (each column on the screen)
        ray_width = self.width/ self.num_rays 
        pos_x = self.count * ray_width
        # Calculate where to draw the line vertically
        top = (self.height - line_height)/2
        bottom = top + line_height
        final_color = self.apply_ambient_light(ray_length)

        # Draw the vertical slice representing the wall
        self.canvas.create_line( pos_x, top,  pos_x, bottom, fill=final_color, width =ray_width*1.08164, tag = "wall")

                
        self.count +=1 
        if self.count >=self.num_rays:
            self.count =0  
        
    def cast_ray(self, player_x, player_y, ray_angle):
        # Calculate the direction of the ray
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        # Initialize the ray's starting position
        ray_x = player_x 
        ray_y = player_y
        
        while True:
            # Calculate the grid cell the ray is in
            grid_x = int(ray_x // self.tile_size)
            grid_y = int(ray_y // self.tile_size)
            # Check if the ray is outside the map bounds
            if grid_x < 0 or grid_y < 0 or grid_x >= len(self.map[0]) or grid_y >= len(self.map):
                break

            # Check if the ray has hit a wall
            if self.map[grid_y][grid_x] == 1:  # Wall
                #print(f"Ray hit a wall at grid cell ({grid_x}, {grid_y})")
                #self.canvas.create_line( player_x, player_y,  ray_x, ray_y, fill="yellow", width =1)
                self.draw_2D_World(ray_x,ray_y,ray_angle)  
                
                return (grid_x, grid_y)
                
            # Move the ray forward by a small amount
            ray_x += ray_dir_x * 0.4
            ray_y += ray_dir_y * 0.4

# Main part of the application

map_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

root = tk.Tk()
game = Game(root, map_data)
root.mainloop()