#version 120

varying vec2 texCoord;
varying vec3 Normal;
varying vec3 FragPos;

uniform sampler2D texture0;
uniform vec3 lightPos;
uniform vec3 viewPos;

void main()
{
    float ambientStrength = 1.0;
    vec3 lightColor = vec3(1.0, 1.0, 1.0);

    // Используем texture2D вместо texture
    vec4 texColor = texture2D(texture0, texCoord);
    vec3 color = texColor.rgb;
    vec3 ambient = ambientStrength * lightColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);

    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    float specularStrength = 10.0;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);

    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = specularStrength * spec * lightColor;

    vec3 result = (ambient + diffuse + specular) * color;
    gl_FragColor = vec4(result, 1.0);  // Используем gl_FragColor вместо outputColor
}