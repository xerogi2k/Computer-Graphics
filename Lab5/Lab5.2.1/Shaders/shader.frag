#version 460 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
in vec2 texCoord;
in float FogFactor;

out vec4 FragColor;

uniform int useMultiTexturing;
uniform int fogEnabled;
uniform sampler2D texture0;
uniform sampler2D texture1;
uniform vec3 fogColor = vec3(0.5, 0.5, 0.5);

void main()
{
    vec4 texColor0 = texture(texture0, texCoord);

    if (useMultiTexturing == 1)
    {
        vec4 texColor1 = texture(texture1, texCoord);
        vec3 mixedColor = mix(texColor0.rgb, texColor1.rgb, 0.5);
        vec3 finalColor = fogEnabled == 1 ? mix(fogColor, mixedColor, FogFactor) : mixedColor;
        FragColor = vec4(finalColor, texColor0.a);
    }
    else
    {
        vec3 finalColor = fogEnabled == 1 ? mix(fogColor, texColor0.rgb, FogFactor) : texColor0.rgb;
        FragColor = vec4(finalColor, texColor0.a);
    }
}