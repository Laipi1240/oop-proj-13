import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer

class Level:
    def __init__(self):
    
    	# get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        
    	#attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        
    	#sprite setup
        self.create_map()

        #user interface
        self.ui = UI()
        
        #particles
        self.animation_player = AnimationPlayer()

    def create_attack(self):
        self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None
    def create_magic(self,style,strength,cost):
        print(style)
        print(strength)
        print(cost)
    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('/home/kyd/group13_project/cool/01_Block.csv'),
            '01': import_csv_layout('/home/kyd/group13_project/cool/01_配件.csv'),
            '02': import_csv_layout('/home/kyd/group13_project/cool/01_物件.csv'),
            'entity': import_csv_layout('/home/kyd/group13_project/cool/01_enemy.csv'),
            'player': import_csv_layout('/home/kyd/group13_project/cool/01_Player.csv') 
        }
        graphics = {
            '01':import_folder('/home/kyd/group13_project/graphics/pic'),
            'ob':import_folder('/home/kyd/group13_project/graphics/pic')
        }
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible')
                        if style == '01':
                            random_grass_image = choice(graphics['01'])
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],'01',random_grass_image)    
                        if style == '02':
                            random_grass_image = choice(graphics['01'])
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites] ,'02',random_grass_image)
                        if style == 'ob': 
                            surf = graphics['ob'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'ob',surf)
                        if style == 'player':
                            self.player = Player((x,y),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack,self.create_magic)
                        if style == 'entity':
                            Enemy('bamboo',(x,y),[self.visible_sprites,self.attackable_sprites],self.obstacle_sprites,self.damage_player,self.trigger_death_particles)         

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites =pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type =='01'or target_sprite.sprite_type =='02':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,60)
                            for leaf in range(randint(3,6)):        
                                self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player,attack_sprite.sprite_type)
 
        
    def damage_player(self,amount,attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])
    def trigger_death_particles(self,pos,particle_type):
        self.animation_player.create_particles(particle_type,pos,self.visible_sprites)
        
    def run(self):
        #update and draw the pygame
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        
        #creating the floor
        floor_surf = pygame.image.load('/home/kyd/group13_project/cool/03.png').convert()
        self.floor_surf = pygame.transform.scale(floor_surf,(1280*4,800*4))
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
        
    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') if sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
    
    
           
    def custom_draw(self,player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        
        #drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf,floor_offset_pos)
        
        #for sprite in self.sprites()
        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset 
            self.display_surface.blit(sprite.image,offset_pos)
            
