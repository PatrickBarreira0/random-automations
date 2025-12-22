if game.CoreGui:FindFirstChild("MineToggleUI") then
    game.CoreGui.MineToggleUI:Destroy()
end
getgenv().AutoMineEnabled = false 

local WANTED_ORES = {
    ["Silver"] = true,
    ["Gold"] = true,
    ["Diamond"] = true,
    ["Ruby"] = true,
    ["Sapphire"] = true,
    ["Emerald"] = true
}

local TRASH_ORES = {
    ["Iron"] = true,
    ["Stone"] = true,
    ["Coal"] = true,
    ["Copper"] = true
}

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local player = Players.LocalPlayer

local ToolRemote = nil
pcall(function()
    ToolRemote = RS.Shared.Packages.Knit.Services.ToolService.RF.ToolActivated
end)

if not ToolRemote then
    return
end

--  MINING LOGIC
function GetOreType(rockModel)
    for _, child in pairs(rockModel:GetDescendants()) do
        local ore = child:GetAttribute("Ore")
        if ore then return ore end
    end
    local mainOre = rockModel:GetAttribute("Ore")
    if mainOre then return mainOre end
    return nil
end

function MineRock(rock)
    if not getgenv().AutoMineEnabled then return end
    
    local char = player.Character
    if not char or not char:FindFirstChild("HumanoidRootPart") then return end
    local root = char.HumanoidRootPart

    -- Teleport
    root.CFrame = rock:GetPivot() * CFrame.new(0, 0, 4)
    task.wait(0.2)
    
    local oreType = nil
    local attempts = 0
    
    -- Hit to Reveal
    while rock.Parent and attempts < 15 and getgenv().AutoMineEnabled do
        ToolRemote:InvokeServer("Pickaxe")
        attempts = attempts + 1
        oreType = GetOreType(rock)
        if oreType then break end
        task.wait(0.25)
    end
    
    -- Decide
    if oreType then
        if WANTED_ORES[oreType] then
            -- Keep mining
            while rock.Parent and getgenv().AutoMineEnabled do
                ToolRemote:InvokeServer("Pickaxe")
                task.wait(0.1)
            end
        elseif TRASH_ORES[oreType] then
            -- Trash: Stop immediately
            return
        else
            -- Unknown: Take it anyway
            while rock.Parent and getgenv().AutoMineEnabled do
                ToolRemote:InvokeServer("Pickaxe")
                task.wait(0.1)
            end
        end
    end
end

function StartLoop()
    task.spawn(function()
        while getgenv().AutoMineEnabled do
            pcall(function()
                local char = player.Character
                if not char then return end
                local root = char:FindFirstChild("HumanoidRootPart")
                if not root then return end
                
                local target = nil
                local minDist = 100 
                
                for _, obj in pairs(workspace:GetDescendants()) do
                    if (obj.Name == "Rock" or obj.Name == "Ore" or string.find(obj.Name, "Node")) and obj:IsA("Model") then
                        local h = obj:GetAttribute("Health")
                        if (h and h > 0) or (not h) then 
                             local dist = (obj:GetPivot().Position - root.Position).Magnitude
                             if dist < minDist then
                                 minDist = dist
                                 target = obj
                             end
                        end
                    end
                end
                
                if target then
                    MineRock(target)
                end
            end)
            task.wait(0.5)
        end
    end)
end

local ScreenGui = Instance.new("ScreenGui")
local ToggleBtn = Instance.new("TextButton")
local UICorner = Instance.new("UICorner")

ScreenGui.Name = "MineToggleUI"
ScreenGui.Parent = game.CoreGui

ToggleBtn.Name = "Toggle"
ToggleBtn.Parent = ScreenGui
ToggleBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
ToggleBtn.Position = UDim2.new(0.5, -75, 0.1, 0)
ToggleBtn.Size = UDim2.new(0, 150, 0, 50)
ToggleBtn.Font = Enum.Font.GothamBold
ToggleBtn.Text = "BOT: OFF"
ToggleBtn.TextColor3 = Color3.new(1, 1, 1)
ToggleBtn.TextSize = 20

UICorner.CornerRadius = UDim.new(0, 8)
UICorner.Parent = ToggleBtn

ToggleBtn.MouseButton1Click:Connect(function()
    getgenv().AutoMineEnabled = not getgenv().AutoMineEnabled
    
    if getgenv().AutoMineEnabled then
        ToggleBtn.Text = "BOT: ON"
        ToggleBtn.BackgroundColor3 = Color3.fromRGB(50, 200, 50)
        StartLoop()
    else
        ToggleBtn.Text = "BOT: OFF"
        ToggleBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    end
end)