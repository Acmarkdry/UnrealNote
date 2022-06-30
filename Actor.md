## Actor相关函数

## Character

初始化

```python
    def __init__(self):
        '''此方法会在MyActor实例构造（NewObject<MyActor>()）时调用'''
        self.PrimaryActorTick.bCanEverTick = True
        
        # 设置胶囊体组件的尺寸（胶囊体用于碰撞）
        capsule_comp = self.CapsuleComponent
        capsule_comp.CapsuleRadius = 42.0
        capsule_comp.CapsuleHalfHeight = 96.0

        # 此类自己拥有的属性为小写+下划线
        self.base_turn_rate = 45.0
        self.base_lookup_rate = 45.0

        # 不使用Controller的旋转
        self.bUseControllerRotationPitch = False
        self.bUseControllerRotationYaw = False
        self.bUseControllerRotationRoll = False

        # 设置移动组件的属性
        char_move_comp = self.CharacterMovement
        # 始终朝向自己移动的方向
        char_move_comp.bOrientRotationToMovement = True
        char_move_comp.RotationRate = ue.Rotator(0.0, 540.0, 0.0)
        char_move_comp.JumpZVelocity = 600.0
        char_move_comp.AirControl = 0.2

        # 注意！！
        # AddActorComponent 里自带ReigsterComponent等需要操作
        # 它的调用时机是在ReceiveBeginPlay里，若放到__init__会有异常
        # 如果增加Component想放到__init__里，应该使用 CreateDefaultSubobject
        self.camera_boom = self.CreateDefaultSubobject(ue.SpringArmComponent.Class(), "CameraBoom")
        self.camera_boom.SetupAttachment(self.RootComponent)
        self.camera_boom.TargetArmLength = 100
        self.camera_boom.bUsePawnControlRotation = True # 这里设置的是镜头

        self.follow_camera = self.CreateDefaultSubobject(ue.CameraComponent.Class(), "FollowCamera") #type:ue.CameraComponent
        self.follow_camera.SetupAttachment(self.camera_boom)
        self.follow_camera.SetRelativeLocation(ue.Vector(-300,0,100))
        self.follow_camera.bUsePawnControlRotation = False

        # 设置Mesh资源
        self.Mesh.SetSkeletalMesh(
            ue.LoadObject(ue.SkeletalMesh.Class(), '/Game/Character/UE4_Mannequin/Mesh/SK_Mannequin.SK_Mannequin')) #type:ue.SkeletalMeshComponent

        # 资源匹配胶囊体大小，适配朝向
        self.Mesh.SetRelativeLocation(ue.Vector(0.0, 0.0, -97.0))
        self.Mesh.SetRelativeRotation(ue.Rotator(0.0, 270, 0.0))

        self.Mesh.AnimationMode = ue.EAnimationMode.AnimationBlueprint  # 使用动画蓝图
        # 注意LoadClass参数的Path需要加上"_C"
        anim_bp_class = ue.LoadClass('/Game/CharacterBP/SurvivorChatacterAnim.SurvivorChatacterAnim_C')
        # 设置Mesh使用的蓝图蓝图类具体是哪个
        self.Mesh.SetAnimClass(anim_bp_class)

        self.Mesh.SetCollisionEnabled(ue.ECollisionEnabled.QueryOnly)
        self.Mesh.SetCollisionObjectType(ue.ECollisionChannel.ECC_Pawn)
        self.Mesh.SetCollisionResponseToAllChannels(ue.ECollisionResponse.ECR_Block)

        self.WeaponMesh = self.CreateDefaultSubobject(ue.SkeletalMeshComponent.Class(),"Weapon") #type:ue.SkeletalMeshComponent
        self.WeaponMesh.SetupAttachment(self.RootComponent)
        self.WeaponMesh.SetSkeletalMesh(ue.LoadObject(ue.SkeletalMesh.Class(),'/Game/Weapon/Meshes/Ka47/SK_KA47_X.SK_KA47_X'),True)

        self.HPComponent = self.CreateDefaultSubobject(ue.WidgetComponent.Class(),'HPBar') #type:ue.WidgetComponent
        #self.HPBar = None
        self.HPComponent.SetupAttachment(self.RootComponent)
        self.HPComponent.SetRelativeLocation(ue.Vector(0,0,0))

        self.FireMontangeContinue = ue.LoadObject(ue.AnimMontage.Class(),'/Game/CharacterBP/FIre_Continue_anim.FIre_Continue_anim') #type:ue.AnimMontage
```

ReceiveBeginplay的设置

```python
    def ReceiveBeginplay(self):
        self.NowWeapon = None
        self.WeaponList = []

        self.WeaponMesh.AttachToComponent(self.GetMesh(),"Weapon_socket",ue.EAttachmentRule.SnapToTarget,ue.EAttachmentRule.SnapToTarget,ue.EAttachmentRule.SnapToTarget,True)

        self.CharMove = self.CharacterMovement #type:ue.CharacterMovementComponent
        self.CharMove.bOrientRotationToMovement = False
        self.CharMove.bUseControllerDesiredRotation = True
        self.CharMove.MaxWalkSpeed = 250

        self.gameModePoint = ue.GameplayStatics.GetGameMode(self)
```

事件绑定

```python
        input_comp = self.GetWorld().GetPlayerController().InputComponent

        input_comp.BindAction("Jump", ue.EInputEvent.IE_Pressed, self.Jump)
        input_comp.BindAction("Jump", ue.EInputEvent.IE_Released, self.StopJumping)

        input_comp.BindAxis("MoveForward", self.move_forward)
        input_comp.BindAxis("MoveRight", self.move_right)
            def move_forward(self,value):
        # todo:给武器设置第一次拾取之后无法再被拾取 添加一个 bool 变量
        controler = self.Controller
        rotation = controler.GetControlRotation()
        yaw_rotation = ue.Rotator(0,rotation.Yaw,0)
        direction = ue.KismetMathLibrary.GetForwardVector(yaw_rotation)
        self.AddMovementInput(direction,value)

    def move_right(self,value):
        controller = self.Controller
        rotation = controller.GetControlRotation()
        yaw_rotation = ue.Rotator(0,rotation.Yaw,0)
        direction = ue.KismetMathLibrary.GetRightVector(yaw_rotation)
        self.AddMovementInput(direction,value)

    def turn_at_rate(self,rate):
        delta_seconds = ue.GameplayStatics.GetWorldDeltaSeconds(self.GetWorld())
        self.AddControllerYawInput(rate*self.base_turn_rate*delta_seconds)

        
```

```python
self.GetVelocity() # 获取当前速度
vector = self.GetActorLocation() # 获取人物当前的位置
rotation = self.GetActorRotation() # 获取人物当前的旋转
                self.SpawnMissileSound = ue.LoadObject(ue.SoundBase.Class(),'/Game/Sounds/GenerateMissileSound.GenerateMissileSound')
                ue.GameplayStatics.PlaySoundAtLocation(self.GetWorld(),self.SpawnMissileSound,self.GetActorLocation(),self.GetActorRotation())
# 播放音乐
animTime = self.PlayAnimMontage(self.ChangeWeaponAnim,1) # 播放蒙太奇 其中1代表播放一遍，-1代表一直播放，但是这里1也不会停止，单纯的代表速率，所以需要通过定时器来自动关闭播放

ue.KismetMathLibrary.GetForwardVector(rotation) # 获取rotation的单位向量
```

widgetComponent

```python
        self.HPComponent.SetRelativeLocation(ue.Vector(-5,-180,-120))
        self.HPComponent.SetWidget(self.widget)
        self.HPComponent.SetWidgetSpace(ue.EWidgetSpace.World)
```

## GameModeBase

```python
        ue_world = self.GetWorld()
        rotation = ue.Rotator(0,0,0)
        location = ue.Vector(250,-430,60)
        weapon_actor = ue_world.SpawnActor(AWeaponBase,location,rotation) #type:ue.Actor
        weapon_actor.SetActorLocationAndRotation(location,rotation,False,False)
 # 插入人物

        self.characterActor.AutoPossessPlayer = ue.EAutoReceiveInput.Player0
        self.characterActor.SetupPlayerInputComponent()
        # 设置本地操纵的人物
```

## ue_site

```python
	def on_tick(self, delta_seconds):
		'''如有定义，则每帧调用。'''
		TimerManager.scheduler() # 实现定时器
```

在import_preload_subclassing中添加要导入的文件，其中需要注意循环引用

在其他类中如何获取到这个ue_site

```python
            gameInstance = ue.GameplayStatics.GetGameInstance(self)

            ueSite = gameInstance.GetPyProxy()
        ue.GameplayStatics.OpenLevel(self.GetWorld(),'IdleMap') # 切换地图
```

创建ui

```python
    def SpawnFightUI(self):
        from UI import FightUIBase
        from UI.utils import UILibrary

        world = self.GetWorld()
        controller = world.GetPlayerController()
        rootWidget = FightUIBase.init_root(world,controller)
        self.SurvivorUI = UILibrary.create_ui(world,controller,rootWidget.GetRootWidget(),FightUIBase.FightUIPanel) #type:FightUIBase.FightUIPanel

```

