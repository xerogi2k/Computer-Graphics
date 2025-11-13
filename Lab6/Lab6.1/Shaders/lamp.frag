#version 120

varying vec2 texCoord;

uniform sampler2D texture0;

void main()
{
    // Используем texture2D и gl_FragColor
    gl_FragColor = texture2D(texture0, texCoord);
}