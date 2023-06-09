'use strict';


const clamp = (x, min, max) => x < min ? min : x > max ? max : x
const randRange = (min, max) => Math.random() * (max - min) + min


class Vec2 {
    constructor(x, y) {
        this.x = x
        this.y = y
    }

    static fromPolar(angle, norm) {
        return new Vec2(Math.cos(angle) * norm, Math.sin(angle) * norm)
    }

    add(other) {
        return new Vec2(this.x + other.x, this.y + other.y)
    }
    radd(other) {
        this.x += other.x
        this.y += other.y
        return this
    }
    mult(scalar) {
        return new Vec2(this.x * scalar, this.y * scalar)
    }
    dividedBy(scalar) {
        return new Vec2(this.x / scalar, this.y / scalar)
    }
    to(other) {
        return new Vec2(other.x - this.x, other.y - this.y)
    }

    dot(other) {
        return this.x * other.x + this.y * other.y
    }
    norm2() {
        return this.x * this.x + this.y * this.y
    }
    norm() {
        return Math.sqrt(this.norm2())
    }
    eq(other) {
        return this.x === other.x && this.y === other.y
    }

    copy() {
        return new Vec2(this.x, this.y)
    }
    toString() {
        return `Vec2(${this.x}, ${this.y})`
    }
}

class Bubble {
    /**
     * A Fancy bubble.
     *
     * @param {Vec2} pos
     * @param {Vec2} vel
     * @param {int} radius
     * @param seed
     */
    constructor(pos, vel, radius, seed=null) {
        radius = Math.floor(radius)
        this.pos = pos;
        this.vel = vel;
        this.radius = radius;
        this.inv_mass = 1 / (radius * radius)

        this.img = null
        this.ready = false
        this.setBubbleImage(seed)
    }
    updatePos(dt) {
        if (!this.ready) return;
        this.pos.radd(this.vel.mult(dt))
    }
    collideBorders(borderSize) {
        if (!this.ready) return;

        if (this.pos.x - this.radius <= 0 && this.vel.x < 0) {
            this.vel.x = -this.vel.x
        } else if (this.pos.x + this.radius >= borderSize.x && this.vel.x > 0 ) {
            this.vel.x = -this.vel.x
        }

        if (this.pos.y - this.radius <= 0 && this.vel.y < 0) {
            this.vel.y = -this.vel.y
        } else if (this.pos.y + this.radius >= borderSize.y && this.vel.y > 0) {
            this.vel.y = -this.vel.y
        }
    }
    collideBubble(other) {
        if (!this.ready || !other.ready) return;

        let dist = this.pos.to(other.pos)
        const dist2 = dist.norm2()
        if (dist2 >= (this.radius + other.radius)**2) {
            // No collisions
            return
        }

        const d = Math.sqrt(dist2)
        let normal, penetration
        if (dist2 !== 0.0) {
            penetration = this.radius + other.radius - d
            normal = dist.dividedBy(d)
        } else {
            penetration = this.radius
            normal = new Vec2(0, 1)
        }

        return new Collision(this, other, normal, penetration)
    }
    collideRect(rect) {
        if (!this.ready) return;

        // Find the closest point to the circle within the rectangle
        const closest = new Vec2(
            clamp(this.pos.x, rect.min.x, rect.max.x),
            clamp(this.pos.y, rect.min.y, rect.max.y)
        )

        // Calculate the distance between the circle's center and this closest point
        let d = closest.to(this.pos)

        // If the distance is less than the circle's radius, an intersection occurs
        const norm2 = d.norm2()
        if (norm2 >= (this.radius * this.radius)) {
            return
        }

        const norm = Math.sqrt(norm2)

        if (closest.eq(this.pos)) {
            // Circle is inside the AABB, so we need to clamp the circle's center
            // to the closest edge

            const left = this.pos.x - rect.min.x
            const top = this.pos.y - rect.min.y
            const right = rect.max.x - this.pos.x
            const bottom = rect.max.y - this.pos.y

            const mini = Math.min(left, top, right, bottom)
            if (mini === left) {
                closest.x = rect.min.x
            } else if (mini === right) {
                closest.x = rect.max.x
            } else if (mini === top) {
                closest.y = rect.min.y
            } else if (mini === bottom) {
                closest.y = rect.max.y
            }

            const normal = this.pos.to(closest)

            const n = normal.norm();
            return new Collision(this, rect, normal.dividedBy(-n), this.radius - n)
        } else {
            return new Collision(this, rect, d.dividedBy(-norm), this.radius - norm);
        }
    }

    setBubbleImage(seed) {
        this.img = new Image()
        this.img.addEventListener("load", () => {
            const tmpCanvas = document.createElement("canvas")
            const tmpCtx = tmpCanvas.getContext("2d")

            tmpCanvas.width = 2 * this.radius
            tmpCanvas.height = 2 * this.radius
            const grad = tmpCtx.createRadialGradient(
                this.radius, this.radius, this.radius/2,
                this.radius, this.radius, this.radius,
            )
            grad.addColorStop(0.8, "#fff")
            grad.addColorStop(1.0, "rgba(255, 255, 255, 0)")
            tmpCtx.save()
            tmpCtx.fillStyle = grad
            tmpCtx.fillRect(0, 0, tmpCanvas.width, tmpCanvas.height)
            tmpCtx.globalCompositeOperation = "source-in"
            const sh = this.img.height
            const sx = (this.img.width - sh) / 2
            tmpCtx.drawImage(this.img, sx, 0, sh, sh, 0, 0, this.radius * 2, this.radius * 2)
            tmpCtx.restore()
            this.img.addEventListener("load", () => { this.ready = true}, {once: true})
            this.img.src = tmpCanvas.toDataURL("image/png")
            tmpCanvas.remove()
        }, {once: true})
        if (seed === null) {
            seed = Math.floor(randRange(0, 10000))
        }

        this.img.src = `/img/${seed}.png?size=${2 * this.radius}`

    }
    clear(ctx) {
        if (!this.ready) return
        const side = this.radius + 1;
        ctx.clearRect(
            this.pos.x - side, this.pos.y - side,
            2 * side, 2 * side
        )
    }
    render(ctx) {
        if (!this.ready) return;
        ctx.drawImage(this.img, this.pos.x - this.radius, this.pos.y - this.radius)
    }
}

class Rect {
    /**
     * An AABB.
     * @param min
     * @param max
     */
    constructor(min, max) {
        this.min = min
        this.max = max
        this.inv_mass = 0
        this.vel = new Vec2(0, 0)
    }
}

class Collision {
    constructor(objA, objB, normal, penetration) {
        this.objA = objA;
        this.objB = objB;
        this.normal = normal;
        this.penetration = penetration;
    }
    resolve() {
        const velRelative = this.objA.vel.to(this.objB.vel)
        const velAlongNormal = velRelative.dot(this.normal)

        if (velAlongNormal > 0) {
            return
        }

        const j = -2 * velAlongNormal / (this.objA.inv_mass + this.objB.inv_mass)
        const impulse = this.normal.mult(j)
        this.objA.vel.radd(impulse.mult(-this.objA.inv_mass))
        this.objB.vel.radd(impulse.mult(this.objB.inv_mass))
    }
}

class Animation {
    constructor(bubbles_nb, canvasId, ) {
        this.spawns_left = bubbles_nb
        this.bubbles = []
        this.hitboxes = []
        this.last = performance.now()
        this.canvas = document.getElementById(canvasId)
        this.ctx = this.canvas.getContext("2d")


        // All the handles for cleanup
        this.spawn_handle = null
        this.animation_handle = null
    }

    spawn_one(left) {
        if (this.spawns_left-- > 0) {
            let radius, pos, vel
            if (window.innerWidth < 640) {
                radius = randRange(12, 24)
                pos = new Vec2(
                    left ? -radius - 10 : this.canvas.width + radius + 10,
                    this.canvas.height / 2
                )
                vel = Vec2.fromPolar(
                    randRange(1/3, -1/3) * Math.PI,
                    randRange(90, 140)
                )
            } else {
                radius = randRange(15, 35)
                pos = new Vec2(
                    left ? -radius - 10 : this.canvas.width + radius + 10,
                    this.canvas.height + radius + 10
                )
                vel = Vec2.fromPolar(
                    randRange(1 / 6, 2 / 6) * Math.PI,
                    randRange(90, 140)
                )
            }


            this.bubbles.push(new Bubble(pos, vel, radius))
        }
    }

    spawn() {
        if (this.spawns_left <= 0) {
            clearInterval(this.spawn_handle)
            return
        }
        this.spawn_one(true)
        this.spawn_one(false)
    }

    update_hitboxes() {
        this.hitboxes = []  // Clear
        document
            .querySelectorAll(".hitbox")
            .forEach(h => {
                const r = h.getBoundingClientRect()
                this.hitboxes.push(new Rect(
                    new Vec2(r.left, r.top),
                    new Vec2(r.left + r.width, r.top + r.height)
                ))
            })

        this.canvas.width = window.innerWidth
        this.canvas.height =  window.innerHeight
    }

    update(dt) {
        const borderSize = new Vec2(window.innerWidth, window.innerHeight)
        for (const bubble of this.bubbles) {
            bubble.updatePos(dt)
            bubble.collideBorders(borderSize)
        }

        let collisions = []
        this.bubbles.forEach((b1, idx1) => {
            this.bubbles.forEach((b2, idx2) => {
                if (idx2 > idx1) {
                    const col = b1.collideBubble(b2)
                    if (col) {
                        collisions.push(col)
                    }
                }
            })

            this.hitboxes.forEach(hitbox => {
                const col = b1.collideRect(hitbox)
                if (col) {
                    collisions.push(col)
                }
            })
        })
        collisions.forEach(col => {
            col.resolve()
        })

        for (const b of this.bubbles) {
            if (b.pos.x != b.pos.x) {
                // We have a NaN :/
                console.log(b)
                debugger;
                return
            }
        }
    }

    render() {
        this.bubbles.forEach(bubble => bubble.render(this.ctx))
    }

    animation_frame(now) {
        // We cap dt at 0.1
        const dt = Math.min(0.1, (now - this.last) / 1000)
        this.bubbles.forEach(b => b.clear(this.ctx))
        this.update(dt)
        this.render()

        this.last = now
        this.animation_handle = requestAnimationFrame(this.animation_frame.bind(this))

    }
    start() {
        this.update_hitboxes()
        this.spawn_handle = setInterval(this.spawn.bind(this), 1000)
        window.addEventListener("resize", this.update_hitboxes.bind(this))
        this.last = performance.now()
        requestAnimationFrame(this.animation_frame.bind(this))

    }

    stop() {
        window.removeEventListener("resize", this.update_hitboxes.bind(this))
        clearInterval(this.spawn_handle)
        cancelAnimationFrame(this.animation_handle)
    }
}
