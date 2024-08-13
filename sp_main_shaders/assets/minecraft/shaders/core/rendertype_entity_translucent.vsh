#version 150

#moj_import <light.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;

uniform float GameTime;
uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

out float vertexDistance;
out vec4 vertexColor;
out vec4 lightMapColor;
out vec4 overlayColor;
out vec2 texCoord0;
out vec4 normal;

flat out int skinEffects;
flat out int isFace;
flat out vec3 Times;

void main() {
    // AdamRG45 Note (4 апреля 2024):
    // Кто автор этих шейдеров и что они делают? Есть предположение
    // что фиксят Ears мод, но это не точно. Эти шейдеры были тут
    // ещё во времена Енотиса, Еврозд их удалять не стал, я тоже
    // удалять не буду.


    //skin effects
    skinEffects = 0;
    isFace = 0;
    vec4 skindata = texture(Sampler0, vec2(0.5, 0.0));
    vec4 skindata_2 = texture(Sampler0, vec2(0.9375, 0.75));
    //face vertices
    if(((gl_VertexID >= 16 && gl_VertexID < 20) || (gl_VertexID >= 160 && gl_VertexID < 164))) {
        isFace = 1;
    }
    //enable blink
    if (abs(skindata.a - 0.918) < 0.001) {
        skinEffects = 1;
        Times = skindata.rgb;
    }
    //234 альфа несовместим с Around ушами.
    if (abs(skindata_2.a - 0.918) < 0.001) {
        skinEffects = 2;
        Times = skindata_2.rgb;
    }
    //128 альфа несовместим с Claws and Horn выступами
    if (abs(skindata_2.a - 0.502) < 0.001) {
        skinEffects = 3;
        Times = skindata_2.rgb;
    }
    //120 альфа несовместим с Horn выступами
    if (abs(skindata_2.a - 0.471) < 0.001) {
        skinEffects = 4;
        Times = skindata_2.rgb;
    }
    //110 альфа несовместим с Claws выступами
    if (abs(skindata_2.a - 0.432) < 0.001) {
        skinEffects = 5;
        Times = skindata_2.rgb;
    }

    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);
    normal = ProjMat * ModelViewMat * vec4(Normal, 0.0);
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color);
    vertexDistance = length((ModelViewMat * vec4(Position, 1.0)).xyz);
    lightMapColor = texelFetch(Sampler2, UV2 / 16, 0);
    overlayColor = texelFetch(Sampler1, UV1, 0);
    texCoord0 = UV0;
}