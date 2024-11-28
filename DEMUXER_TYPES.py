DEMUXER_TYPES = {
    'video': [
        '3dostr', '4xm', 'avi', 'av1', 'avs', 'avs2', 'avs3', 'bink', 'binka', 'bmv',
        'cavsvideo', 'dfa', 'dirac', 'dnxhd', 'dv', 'dxa', 'ffv1', 'film_cpk', 'flic',
        'flv', 'h261', 'h263', 'h264', 'hevc', 'hnm', 'ipmovie', 'ivf', 'mjpeg',
        'mjpeg_2000', 'mpeg', 'mpegts', 'mpegvideo', 'mv', 'mvi', 'mxf', 'nsv', 'nuv',
        'pmp', 'rl2', 'roq', 'smk', 'swf', 'vc1', 'viv', 'vmd', 'yuv4mpegpipe',
        'asf', 'matroska,webm', 'mov,mp4,m4a,3gp,3g2,mj2', 'mxf', 'nut', 'wtv'
    ],
    
    'audio': [
        'aac', 'ac3', 'act', 'aiff', 'alp', 'amr', 'amrnb', 'amrwb', 'ape', 'au',
        'codec2', 'dts', 'eac3', 'flac', 'gsm', 'hca', 'mlp', 'mp3', 'mpc', 'mpc8',
        'msf', 'mulaw', 'oma', 'opus', 'paf', 'qcp', 'rso', 'sbc', 'shn', 'tak',
        'tta', 'voc', 'w64', 'wav', 'wv', 'xa'
    ],
    
    'image': [
        'apng', 'bmp_pipe', 'dpx_pipe', 'exr_pipe', 'gif', 'gif_pipe', 'ico',
        'jpeg_pipe', 'jpegls_pipe', 'jpegxl_pipe', 'pam_pipe', 'pbm_pipe', 'pcx_pipe',
        'pgm_pipe', 'png_pipe', 'psd_pipe', 'qoi_pipe', 'sgi_pipe', 'sunrast_pipe',
        'svg_pipe', 'tiff_pipe', 'webp_pipe', 'xbm_pipe', 'xpm_pipe', 'xwd_pipe'
    ],
    
    'streaming': [
        'dash', 'hls', 'live_flv', 'mpjpeg', 'rtp', 'rtsp', 'sdp', 'smjpeg',
        'webm_dash_manifest'
    ],
    
    'subtitle': [
        'ass', 'jacosub', 'microdvd', 'mpl2', 'mpsub', 'pjs', 'realtext', 'sami',
        'scc', 'stl', 'srt', 'ssa', 'subviewer', 'subviewer1', 'vplayer', 'webvtt'
    ],
    
    'utility': [
        'concat', 'ffmetadata', 'lavfi', 'framecrc', 'framemd5', 'null', 'tee'
    ],
    
    'game': [
        'bfstm', 'brstm', 'gxf', 'psxstr', 'thp', 'vag', 'vpk', 'xmv'
    ],
    
    'raw': [
        'data', 'f32be', 'f32le', 'f64be', 'f64le', 's16be', 's16le', 's24be',
        's24le', 's32be', 's32le', 's8', 'u16be', 'u16le', 'u24be', 'u24le',
        'u32be', 'u32le', 'u8', 'rawvideo'
    ]
}